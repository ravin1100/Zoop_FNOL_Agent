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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setFormData(prev => ({
        ...prev,
        [name]: checkbox.checked
      }));
    } else if (type === 'number') {
      setFormData(prev => ({
        ...prev,
        [name]: parseFloat(value) || 0
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setIsProcessing(true);
    setProcessingUpdates([]);
    setProcessingComplete(false);

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
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStageIcon = (stage: string, status: string) => {
    if (status === 'done') {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    } else if (status === 'in_progress') {
      return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
    } else {
      return <AlertCircle className="h-5 w-5 text-gray-300" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Submit New Claim</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Claim ID
                </label>
                <input
                  type="text"
                  name="claim_id"
                  value={formData.claim_id}
                  onChange={handleInputChange}
                  placeholder="Auto-generated if empty"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Claim Type *
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
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
                <label className="block text-sm font-medium text-gray-700">
                  Incident Date *
                </label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Claim Amount *
                </label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  required
                  min="0"
                  step="0.01"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                rows={3}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Customer ID *
                </label>
                <input
                  type="text"
                  name="customer_id"
                  value={formData.customer_id}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Policy Number *
                </label>
                <input
                  type="text"
                  name="policy_number"
                  value={formData.policy_number}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Incident Location *
              </label>
              <input
                type="text"
                name="incident_location"
                value={formData.incident_location}
                onChange={handleInputChange}
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Police Report Number
              </label>
              <input
                type="text"
                name="police_report"
                value={formData.police_report || ''}
                onChange={handleInputChange}
                placeholder="Enter police report number (optional)"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Customer Tenure (Days)
                </label>
                <input
                  type="number"
                  name="customer_tenure_days"
                  value={formData.customer_tenure_days || ''}
                  onChange={handleInputChange}
                  min="0"
                  placeholder="Number of days as customer"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Previous Claims Count
                </label>
                <input
                  type="number"
                  name="previous_claims_count"
                  value={formData.previous_claims_count || ''}
                  onChange={handleInputChange}
                  min="0"
                  placeholder="Number of previous claims"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="injuries_reported"
                  checked={formData.injuries_reported || false}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Injuries reported
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="other_party_involved"
                  checked={formData.other_party_involved || false}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Other party involved
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || isProcessing}
              className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Clock className="animate-spin -ml-1 mr-3 h-5 w-5" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="-ml-1 mr-3 h-5 w-5" />
                  Submit Claim
                </>
              )}
            </button>
          </form>
        </div>

        {/* Processing Status */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Processing Status</h3>
          
          {!isProcessing && processingUpdates.length === 0 && !processingComplete && (
            <div className="text-center text-gray-500 py-8">
              <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">Submit a claim to see processing status</p>
            </div>
          )}

          {(isProcessing || processingUpdates.length > 0) && (
            <div className="space-y-4">
              {['Parsing claim', 'Assessing risk', 'Deciding routing'].map((stageName) => {
                const update = processingUpdates.find(u => u.stage === stageName);
                const status = update?.status || 'pending';
                
                return (
                  <div key={stageName} className="flex items-center space-x-3">
                    {getStageIcon(stageName, status)}
                    <span className={`text-sm ${
                      status === 'done' ? 'text-green-700' :
                      status === 'in_progress' ? 'text-blue-700' :
                      'text-gray-500'
                    }`}>
                      {stageName}
                    </span>
                  </div>
                );
              })}
              
              {processingComplete && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">
                        Claim Processing Complete!
                      </h3>
                      <p className="mt-2 text-sm text-green-700">
                        Your claim has been successfully processed and routed to the appropriate adjuster.
                      </p>
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