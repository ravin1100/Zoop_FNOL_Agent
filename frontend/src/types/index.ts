// Types for dashboard data
export interface DashboardData {
  total_claims: number;
  processing_stats: {
    total_processed: number;
    fraud_detected: number;
    fraud_rate: number;
    avg_risk_score: number;
  };
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  priority_distribution: {
    normal: number;
    high: number;
    urgent: number;
  };
  adjuster_distribution: {
    tier_1: number;
    tier_2: number;
    tier_3: number;
  };
  claim_type_distribution: {
    auto: number;
    property_damage: number;
    health: number;
    liability: number;
    collision: number;
    comprehensive: number;
    other: number;
  };
  recent_claims: {
    today: number;
    this_week: number;
    this_month: number;
  };
  amount_metrics: {
    total_amount: number;
    average_amount: number;
    highest_amount: number;
    lowest_amount: number;
  };
  recent_activity: RecentActivity[];
  top_claim_types: Record<string, number>;
  high_risk_locations: string[];
}

export interface RecentActivity {
  claim_id: string;
  type: string;
  amount: number;
  risk_level: string;
  priority: string;
  submitted_date: string;
}

// Types for claim submission
export interface ClaimData {
  claim_id: string;
  type: string;
  date: string;
  amount: number;
  description: string;
  customer_id: string;
  policy_number: string;
  incident_location: string;
  timestamp_submitted: string;
  police_report?: string;
  injuries_reported?: boolean;
  other_party_involved?: boolean;
  customer_tenure_days?: number;
  previous_claims_count?: number;
}

// Types for live processing updates
export interface ProcessingUpdate {
  stage: string;
  status: 'in_progress' | 'done' | 'completed';
  claim_id?: string;
}