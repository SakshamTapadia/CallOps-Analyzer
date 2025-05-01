"""
Functions for data processing, including dataset merging and feature engineering.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def merge_call_logs_with_agent_roster(call_logs_df, agent_roster_df):
    """
    Merge call logs with agent roster data.
    
    Args:
        call_logs_df (pd.DataFrame): Call logs DataFrame
        agent_roster_df (pd.DataFrame): Agent roster DataFrame
        
    Returns:
        pd.DataFrame: Merged DataFrame
    """
    logger.info("Merging call logs with agent roster")
    
    # Merge on agent_id and org_id with an indicator to track unmatched rows
    merged_df = pd.merge(
        call_logs_df,
        agent_roster_df,
        on=['agent_id', 'org_id'],
        how='left',
        indicator=True
    )
    
    # Log statistics about the merge
    total_calls = len(call_logs_df)
    matched_calls = (merged_df['_merge'] == 'both').sum()
    unmatched_calls = (merged_df['_merge'] == 'left_only').sum()
    
    logger.info(f"Total calls: {total_calls}")
    logger.info(f"Matched with agent roster: {matched_calls} ({matched_calls/total_calls*100:.2f}%)")
    
    if unmatched_calls > 0:
        logger.warning(f"Unmatched calls: {unmatched_calls} ({unmatched_calls/total_calls*100:.2f}%)")
        
        # Get sample of unmatched agent_ids for debugging
        unmatched_agents = call_logs_df.loc[
            ~call_logs_df['agent_id'].isin(agent_roster_df['agent_id']), 
            'agent_id'
        ].unique()
        
        logger.debug(f"Sample unmatched agent_ids: {unmatched_agents[:5]}")
    
    # Drop the indicator column
    merged_df = merged_df.drop(columns=['_merge'])
    
    return merged_df

def merge_with_disposition_summary(merged_df, disposition_df):
    """
    Merge the combined call logs and agent roster with disposition summary.
    
    Args:
        merged_df (pd.DataFrame): Already merged call logs and agent roster
        disposition_df (pd.DataFrame): Disposition summary DataFrame
        
    Returns:
        pd.DataFrame: Final merged DataFrame
    """
    logger.info("Merging with disposition summary")
    
    # Merge on agent_id, org_id, and call_date with an indicator
    final_df = pd.merge(
        merged_df,
        disposition_df,
        on=['agent_id', 'org_id', 'call_date'],
        how='left',
        indicator=True
    )
    
    # Log statistics about the merge
    total_records = len(merged_df)
    matched_records = (final_df['_merge'] == 'both').sum()
    unmatched_records = (final_df['_merge'] == 'left_only').sum()
    
    logger.info(f"Total records after first merge: {total_records}")
    logger.info(f"Matched with disposition summary: {matched_records} ({matched_records/total_records*100:.2f}%)")
    
    if unmatched_records > 0:
        logger.warning(f"Records without disposition data: {unmatched_records} ({unmatched_records/total_records*100:.2f}%)")
        
        # Group unmatched records by date to see pattern
        if 'call_date' in merged_df.columns:
            unmatched_by_date = merged_df.loc[
                ~final_df['_merge'].isin(['both']), 
                'call_date'
            ].dt.date.value_counts().head()
            
            logger.debug(f"Unmatched records by date: {unmatched_by_date}")
    
    # Drop the indicator column
    final_df = final_df.drop(columns=['_merge'])
    
    return final_df

def calculate_performance_metrics(df):
    """
    Calculate agent performance metrics.
    
    Args:
        df (pd.DataFrame): Merged DataFrame with all data
        
    Returns:
        pd.DataFrame: DataFrame with calculated metrics
    """
    logger.info("Calculating performance metrics")
    
    # Group by agent, organization, date, and agent information
    groupby_cols = ['agent_id', 'org_id', 'call_date', 'users_first_name', 'users_last_name', 'users_office_location']
    
    try:
        # Calculate aggregated metrics
        metrics = pd.DataFrame({
            # Total calls made by agent per day
            'total_calls': df.groupby(groupby_cols).size(),
            
            # Unique loans contacted
            'unique_loans': df.groupby(groupby_cols)['installment_id'].nunique(),
            
            # Count of completed calls (for connect rate)
            'completed_calls': df.groupby(groupby_cols)['status'].apply(
                lambda x: (x == 'completed').sum()
            ),
            
            # Sum of call durations (for average calculation)
            'total_duration_seconds': df.groupby(groupby_cols)['duration'].sum(),
        }).reset_index()
        
        # Calculate connect rate
        metrics['connect_rate'] = (metrics['completed_calls'] / metrics['total_calls']).fillna(0)
        
        # Calculate average call duration in minutes
        metrics['avg_call_duration_minutes'] = (metrics['total_duration_seconds'] / metrics['total_calls'] / 60).fillna(0)
        
        # Format metrics for readability
        metrics['connect_rate_percentage'] = (metrics['connect_rate'] * 100).round(2)
        metrics['avg_call_duration_minutes'] = metrics['avg_call_duration_minutes'].round(2)
        
        # Add presence flag from disposition data
        # First, create a flag indicating if login_time exists for each agent/date combination
        presence_data = df.groupby(['agent_id', 'org_id', 'call_date'])['login_time'].apply(
            lambda x: 1 if x.notna().any() else 0
        ).reset_index()
        
        # Rename the login_time column to presence for clarity
        presence_data = presence_data.rename(columns={'login_time': 'presence'})
        
        # Merge presence data with metrics
        metrics = pd.merge(
            metrics, 
            presence_data, 
            on=['agent_id', 'org_id', 'call_date'], 
            how='left'
        )
        
        # Fill any missing presence values with 0
        metrics['presence'] = metrics['presence'].fillna(0).astype(int)
        
        # Add agent full name for convenience
        metrics['agent_full_name'] = metrics['users_first_name'] + ' ' + metrics['users_last_name']
        
        logger.info(f"Calculated metrics for {len(metrics)} agent-days")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {str(e)}")
        raise