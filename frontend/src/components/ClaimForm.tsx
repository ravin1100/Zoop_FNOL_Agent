'use client';

import { useState } from 'react';
import { ClaimData, ProcessingUpdate } from '@/types';
import { Send, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export default function ClaimForm() {
  const [formData, setFormData] = useState<Partial<ClaimData>>({
    claim_id: '',
    type: 'auto',
    date: '',
    amount: 0,
    description: '',
    customer_id: '',
    policy_number: '',
    incident_location: '',
    police_report: '',
    injuries_reported: false,
    other_party_involved: false,
    customer_tenure_days: 0,
    previous_claims_count: 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [processingUpdates, setProcessingUpdates] = useState<ProcessingUpdate[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});
  const [touched, setTouched] = useState<{[key: string]: boolean}>({});

  const validateField = (name: string, value: any) => {
    switch (name) {
      case 'type':
        return !value ? 'Claim type is required' : '';
      case 'date':
        if (!value) return 'Incident date is required';
        const selectedDate = new Date(value);
        const today = new Date();
        if (selectedDate > today) return 'Incident date cannot be in the future';
        return '';
      case 'amount':
        if (!value || value <= 0) return 'Claim amount must be greater than 0';
        return '';
      case 'description':
        if (!value || value.trim().length < 10) return 'Description must be at least 10 characters';
        return '';
      case 'customer_id':
        return !value || value.trim().length === 0 ? 'Customer ID is required' : '';
      case 'policy_number':
        return !value || value.trim().length === 0 ? 'Policy number is required' : '';
      case 'incident_location':
        return !value || value.trim().length === 0 ? 'Incident location is required' : '';
      default:
        return '';
    }
  };

  const handleInputChange = (e: any) => {
    const { name, value, type } = e.target;
    
    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    if (type === 'checkbox') {
      const checkbox = e.target;
      setFormData((prev: any) => ({
        ...prev,
        [name]: checkbox.checked
      }));
    } else if (type === 'number') {
      setFormData((prev: any) => ({
        ...prev,
        [name]: parseFloat(value) || 0
      }));
    } else {
      setFormData((prev: any) => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleBlur = (e: any) => {
    const { name, value } = e.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));

    const error = validateField(name, value);
    if (error) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  };

  const validateForm = () => {
    const errors: {[key: string]: string} = {};
    const requiredFields = ['type', 'date', 'amount', 'description', 'customer_id', 'policy_number', 'incident_location'];
    
    requiredFields.forEach(field => {
      const error = validateField(field, formData[field as keyof typeof formData]);
      if (error) {
        errors[field] = error;
      }
    });

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      // Mark all fields as touched to show errors
      const allFields = ['type', 'date', 'amount', 'description', 'customer_id', 'policy_number', 'incident_location'];
      const touchedState: {[key: string]: boolean} = {};
      allFields.forEach(field => {
        touchedState[field] = true;
      });
      setTouched(touchedState);
      return;
    }

    setIsSubmitting(true);
    setIsProcessing(true);
    setProcessingUpdates([]);
    setProcessingComplete(false);
    setHasError(false);

    try {
      // Prepare data for submission
      const submitData: ClaimData = {
        ...formData,
        claim_id: formData.claim_id || `CLM-${Date.now()}`,
        timestamp_submitted: new Date().toISOString(),
        amount: Number(formData.amount),
      } as ClaimData;

      // Submit the claim and get streaming response
      const response = await fetch('/api/claims/process-claim-live', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit claim');
      }

      // Read the streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const update: ProcessingUpdate = JSON.parse(line.slice(6));
                
                setProcessingUpdates(prev => {
                  const newUpdates = [...prev];
                  const existingIndex = newUpdates.findIndex(u => u.stage === update.stage);
                  
                  if (existingIndex >= 0) {
                    newUpdates[existingIndex] = update;
                  } else {
                    newUpdates.push(update);
                  }
                  
                  return newUpdates;
                });

                if (update.stage === 'completed') {
                  setProcessingComplete(true);
                  setIsProcessing(false);
                  break;
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e);
              }
            }
          }
        }
      }

    } catch (error) {
      console.error('Error submitting claim:', error);
      setIsProcessing(false);
      setHasError(true);
      // Add a generic error to the processing updates
      setProcessingUpdates(prev => [...prev, {
        stage: 'error',
        status: 'error',
        detail: error instanceof Error ? error.message : 'Failed to submit claim. Please check your connection and try again.'
      }]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderFieldError = (fieldName: string) => {
    if (touched[fieldName] && validationErrors[fieldName]) {
      return (
        <div className="mt-1 text-sm text-red-600 flex items-center">
          <AlertCircle className="h-4 w-4 mr-1" />
          {validationErrors[fieldName]}
        </div>
      );
    }
    return null;
  };

  const getFieldClassName = (fieldName: string, baseClassName: string) => {
    const hasError = touched[fieldName] && validationErrors[fieldName];
    return hasError 
      ? baseClassName.replace('border-gray-300', 'border-red-300').replace('focus:border-primary-500', 'focus:border-red-500').replace('focus:ring-primary-500', 'focus:ring-red-500')
      : baseClassName;
  };

  const getStageIcon = (stage: string, status: string) => {
    if (status === 'done') {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    } else if (status === 'in_progress') {
      return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
    } else if (status === 'error' || stage === 'error') {
      return <AlertCircle className="h-5 w-5 text-red-500" />;
    } else {
      return <AlertCircle className="h-5 w-5 text-gray-300" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 bg-white shadow-xl rounded-xl p-8 border border-gray-100">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Submit New Claim</h2>
            <p className="text-gray-600">Please fill out all required fields to submit your insurance claim.</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claim ID
                </label>
                <input
                  type="text"
                  name="claim_id"
                  value={formData.claim_id || ''}
                  onChange={handleInputChange}
                  onBlur={handleBlur}
                  placeholder="Auto-generated if empty"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claim Type *
                </label>
                <select
                  name="type"
                  value={formData.type || 'auto'}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                >
                  <option value="auto">Auto</option>
                  <option value="property_damage">Property Damage</option>
                  <option value="health">Health</option>
                  <option value="liability">Liability</option>
                  <option value="collision">Collision</option>
                  <option value="comprehensive">Comprehensive</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Incident Date *
                </label>
                <input
                  type="date"
                  name="date"
                  value={formData.date || ''}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claim Amount *
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount || ''}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description || ''}
                onChange={handleInputChange}
                required
                rows={4}
                placeholder="Provide a detailed description of the incident..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white resize-none"
              />
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer ID *
                </label>
                <input
                  type="text"
                  name="customer_id"
                  value={formData.customer_id || ''}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter customer ID"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Number *
                </label>
                <input
                  type="text"
                  name="policy_number"
                  value={formData.policy_number || ''}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter policy number"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Incident Location *
              </label>
              <input
                type="text"
                name="incident_location"
                value={formData.incident_location || ''}
                onChange={handleInputChange}
                required
                placeholder="Enter the location where the incident occurred"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Police Report Number
                <span className="text-gray-500 text-xs ml-1">(Optional)</span>
              </label>
              <input
                type="text"
                name="police_report"
                value={formData.police_report || ''}
                onChange={handleInputChange}
                placeholder="Enter police report number if available"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
              />
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Tenure (Days)
                  <span className="text-gray-500 text-xs ml-1">(Optional)</span>
                </label>
                <input
                  type="number"
                  name="customer_tenure_days"
                  value={formData.customer_tenure_days || ''}
                  onChange={handleInputChange}
                  min="0"
                  placeholder="Number of days as customer"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Previous Claims Count
                  <span className="text-gray-500 text-xs ml-1">(Optional)</span>
                </label>
                <input
                  type="number"
                  name="previous_claims_count"
                  value={formData.previous_claims_count || ''}
                  onChange={handleInputChange}
                  min="0"
                  placeholder="Number of previous claims"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 hover:border-gray-400 transition-colors duration-200 bg-white"
                />
              </div>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg space-y-4">
              <h3 className="text-sm font-medium text-gray-900 mb-4">Additional Information</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    name="injuries_reported"
                    id="injuries_reported"
                    checked={formData.injuries_reported || false}
                    onChange={handleInputChange}
                    className="h-5 w-5 text-primary-600 focus:ring-2 focus:ring-primary-500 border-gray-300 rounded mt-0.5"
                  />
                  <label htmlFor="injuries_reported" className="ml-3 block text-sm text-gray-900 cursor-pointer">
                    <span className="font-medium">Injuries reported</span>
                    <p className="text-gray-500 text-xs mt-1">Check if there were any injuries involved in this incident</p>
                  </label>
                </div>

                <div className="flex items-start">
                  <input
                    type="checkbox"
                    name="other_party_involved"
                    id="other_party_involved"
                    checked={formData.other_party_involved || false}
                    onChange={handleInputChange}
                    className="h-5 w-5 text-primary-600 focus:ring-2 focus:ring-primary-500 border-gray-300 rounded mt-0.5"
                  />
                  <label htmlFor="other_party_involved" className="ml-3 block text-sm text-gray-900 cursor-pointer">
                    <span className="font-medium">Other party involved</span>
                    <p className="text-gray-500 text-xs mt-1">Check if another party was involved in this incident</p>
                  </label>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={isSubmitting || isProcessing}
                className="w-full flex justify-center items-center px-6 py-4 border border-transparent rounded-lg shadow-lg text-base font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                {isSubmitting ? (
                  <>
                    <Clock className="animate-spin -ml-1 mr-3 h-5 w-5" />
                    Submitting Claim...
                  </>
                ) : (
                  <>
                    <Send className="-ml-1 mr-3 h-5 w-5" />
                    Submit Claim
                  </>
                )}
              </button>
              <p className="text-center text-xs text-gray-500 mt-3">
                * Required fields must be filled out before submission
              </p>
            </div>
          </form>
        </div>

        {/* Processing Status */}
        <div className="bg-white shadow-xl rounded-xl p-6 border border-gray-100 h-fit sticky top-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Status</h3>
            <p className="text-sm text-gray-600">Track your claim submission progress</p>
          </div>
          
          {!isProcessing && processingUpdates.length === 0 && !processingComplete && (
            <div className="text-center text-gray-500 py-12">
              <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <AlertCircle className="h-8 w-8 text-gray-400" />
              </div>
              <h4 className="font-medium text-gray-700 mb-2">Ready to Process</h4>
              <p className="text-sm">Submit a claim to see real-time processing status</p>
            </div>
          )}

          {(isProcessing || processingUpdates.length > 0) && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Processing Your Claim</h4>
                <p className="text-sm text-blue-700">Please wait while we analyze your submission...</p>
              </div>
              
              <div className="space-y-4">
                {['Parsing claim', 'Assessing risk', 'Deciding routing'].map((stageName, index) => {
                  const update = processingUpdates.find((u: any) => u.stage === stageName);
                  const status = update?.status || 'pending';
                  
                  return (
                    <div key={stageName} className={`flex items-center space-x-4 p-4 rounded-lg border-2 transition-all duration-300 ${
                      status === 'done' ? 'border-green-200 bg-green-50' :
                      status === 'in_progress' ? 'border-blue-200 bg-blue-50' :
                      status === 'error' ? 'border-red-200 bg-red-50' :
                      'border-gray-200 bg-gray-50'
                    }`}>
                      <div className="flex-shrink-0">
                        {getStageIcon(stageName, status)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className={`font-medium ${
                            status === 'done' ? 'text-green-800' :
                            status === 'in_progress' ? 'text-blue-800' :
                            status === 'error' ? 'text-red-800' :
                            'text-gray-600'
                          }`}>
                            Step {index + 1}: {stageName}
                          </span>
                          <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                            status === 'done' ? 'bg-green-200 text-green-800' :
                            status === 'in_progress' ? 'bg-blue-200 text-blue-800' :
                            status === 'error' ? 'bg-red-200 text-red-800' :
                            'bg-gray-200 text-gray-600'
                          }`}>
                            {status === 'done' ? 'Completed' :
                             status === 'in_progress' ? 'Processing' :
                             status === 'error' ? 'Error' : 'Pending'}
                          </span>
                        </div>
                        {update?.detail && (
                          <p className="text-sm text-gray-600 mt-1">{update.detail}</p>
                        )}
                      </div>
                    </div>
                  );
                })}

              </div>
              
              {/* Display error if any stage has error */}
              {processingUpdates.find((u: any) => u.stage === 'error' || u.status === 'error') && (
                <div className="mt-6 p-6 bg-red-50 border-2 border-red-200 rounded-xl">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <AlertCircle className="h-6 w-6 text-red-500" />
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-base font-semibold text-red-800 mb-2">
                        Error Processing Claim
                      </h3>
                      <p className="text-sm text-red-700 mb-4">
                        {processingUpdates.find((u: any) => u.stage === 'error' || u.status === 'error')?.detail || 
                         'An error occurred while processing your claim. Please check your input and try again.'}
                      </p>
                      <button
                        onClick={() => {
                          setProcessingUpdates([]);
                          setHasError(false);
                          setProcessingComplete(false);
                        }}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {processingComplete && !processingUpdates.find((u: any) => u.stage === 'error' || u.status === 'error') && (
                <div className="mt-6 p-6 bg-green-50 border-2 border-green-200 rounded-xl">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <CheckCircle className="h-6 w-6 text-green-500" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-base font-semibold text-green-800 mb-2">
                        Claim Processing Complete! 🎉
                      </h3>
                      <p className="text-sm text-green-700 mb-3">
                        Your claim has been successfully processed and routed to the appropriate adjuster.
                      </p>
                      <div className="text-xs text-green-600 bg-green-100 px-3 py-1 rounded-full inline-block">
                        Claim ID: {formData.claim_id || 'Generated automatically'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}