'use client';

import { useState } from 'react';
import Navigation from '@/components/Navigation';
import AssessmentsList from '@/components/AssessmentsList';
import { ClaimAssessment } from '@/types';
import { ArrowLeft } from 'lucide-react';

export default function AssessmentsPage() {
  const [selectedAssessment, setSelectedAssessment] = useState<ClaimAssessment | null>(null);

  const handleAssessmentClick = (assessment: ClaimAssessment) => {
    setSelectedAssessment(assessment);
  };

  const handleBackToList = () => {
    setSelectedAssessment(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedAssessment ? (
          <div className="space-y-6">
            {/* Back button */}
            <button
              onClick={handleBackToList}
              className="flex items-center text-primary-600 hover:text-primary-800 mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Assessments List
            </button>
            
            {/* Assessment Detail View */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Claim Assessment Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Claim ID */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Claim ID
                  </label>
                  <div className="bg-gray-50 rounded-md p-3">
                    <span className="text-lg font-mono">{selectedAssessment.claim_id}</span>
                  </div>
                </div>

                {/* Risk Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Risk Level
                  </label>
                  <div className="bg-gray-50 rounded-md p-3">
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                      selectedAssessment.risk_level.toLowerCase() === 'low' ? 'bg-green-100 text-green-800' :
                      selectedAssessment.risk_level.toLowerCase() === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {selectedAssessment.risk_level.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Priority */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority
                  </label>
                  <div className="bg-gray-50 rounded-md p-3">
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                      selectedAssessment.priority.toLowerCase() === 'normal' ? 'bg-blue-100 text-blue-800' :
                      selectedAssessment.priority.toLowerCase() === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {selectedAssessment.priority.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Adjuster Tier */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adjuster Tier
                  </label>
                  <div className="bg-gray-50 rounded-md p-3">
                    <div className="flex flex-wrap gap-2">
                      {selectedAssessment.adjuster_tier.map((tier, index) => (
                        <span 
                          key={index}
                          className="inline-flex px-3 py-1 text-sm font-medium bg-purple-100 text-purple-800 rounded-full"
                        >
                          {tier}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Validation Errors */}
              {selectedAssessment.validation_errors && selectedAssessment.validation_errors.length > 0 && (
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Validation Issues
                  </label>
                  <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <ul className="list-disc list-inside space-y-1">
                      {selectedAssessment.validation_errors.map((error, index) => (
                        <li key={index} className="text-red-800 text-sm">
                          {error}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div className="bg-white shadow rounded-lg p-6">
              <h1 className="text-3xl font-bold text-gray-900">
                Claim Assessments
              </h1>
              <p className="mt-2 text-gray-600">
                View and manage processed claim assessments with risk levels, priorities, and routing decisions.
              </p>
            </div>

            {/* Assessments List */}
            <AssessmentsList onAssessmentClick={handleAssessmentClick} />
          </div>
        )}
      </div>
    </div>
  );
}
