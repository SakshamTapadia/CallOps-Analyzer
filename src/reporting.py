"""
Functions for generating reports, including CSV exports and Slack-style summaries.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def save_performance_summary(metrics_df, output_path):
    """
    Save the agent performance summary to a CSV file.
    
    Args:
        metrics_df (pd.DataFrame): DataFrame with agent performance metrics
        output_path (str): Path to save the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Saving performance summary to {output_path}")
        
        # Select and rename columns for the output
        output_columns = {
            'agent_id': 'agent_id',
            'org_id': 'org_id',
            'call_date': 'date',
            'agent_full_name': 'agent_name',
            'users_office_location': 'office_location',
            'total_calls': 'total_calls',
            'unique_loans': 'unique_loans_contacted',
            'connect_rate': 'connect_rate',
            'avg_call_duration_minutes': 'avg_call_duration_min',
            'presence': 'presence'
        }
        
        # Create a copy with selected and renamed columns
        output_df = metrics_df[list(output_columns.keys())].rename(columns=output_columns)
        
        # Format the connect_rate as a decimal (0.XX)
        output_df['connect_rate'] = output_df['connect_rate'].round(4)
        
        # Format the avg_call_duration_min to 2 decimal places
        output_df['avg_call_duration_min'] = output_df['avg_call_duration_min'].round(2)
        
        # Format the date as YYYY-MM-DD
        output_df['date'] = output_df['date'].dt.strftime('%Y-%m-%d')
        
        # Save to CSV
        output_df.to_csv(output_path, index=False)
        
        logger.info(f"Successfully saved {len(output_df)} records to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving performance summary: {str(e)}")
        return False

def generate_slack_summary(metrics_df, date=None):
    """
    Generate a Slack-style summary message for a specific date.
    
    Args:
        metrics_df (pd.DataFrame): DataFrame with agent performance metrics
        date (str, optional): Date to generate summary for (format: 'YYYY-MM-DD').
                             If None, uses the most recent date in the data.
    
    Returns:
        str: Formatted summary message
    """
    try:
        logger.info("Generating Slack-style summary message")
        
        # If date is not provided, use the most recent date in the data
        if date is None:
            latest_date = metrics_df['call_date'].max()
            date_str = latest_date.strftime('%Y-%m-%d')
        else:
            # Parse the provided date
            date_str = date
            latest_date = pd.to_datetime(date)
        
        # Filter data for the specified date
        daily_data = metrics_df[metrics_df['call_date'] == latest_date].copy()
        
        if daily_data.empty:
            logger.warning(f"No data available for date: {date_str}")
            return f"Agent Summary for {date_str}\nNo data available for this date."
        
        # Find the top performer (agent with highest connect rate who made at least 5 calls)
        valid_agents = daily_data[daily_data['total_calls'] >= 5].copy()
        
        if valid_agents.empty:
            top_performer_name = "N/A"
            top_performer_rate = "N/A"
        else:
            top_performer = valid_agents.loc[valid_agents['connect_rate'].idxmax()]
            top_performer_name = f"{top_performer['users_first_name']} {top_performer['users_last_name']}"
            top_performer_rate = f"{top_performer['connect_rate_percentage']:.0f}%"
        
        # Calculate additional summary statistics
        total_active_agents = daily_data[daily_data['presence'] == 1].shape[0]
        avg_call_duration = daily_data['avg_call_duration_minutes'].mean().round(1)
        
        # Format the summary message
        summary = f"Agent Summary for {date_str}\n"
        summary += f"Top Performer: {top_performer_name} ({top_performer_rate} connect rate)\n"
        summary += f"Total Active Agents: {total_active_agents}\n"
        summary += f"Average Duration: {avg_call_duration} min"
        
        logger.info(f"Summary generated for {date_str}")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"Error generating summary: {str(e)}"

def generate_detailed_report(metrics_df, date=None):
    """
    Generate a more detailed report with agent performance metrics.
    
    Args:
        metrics_df (pd.DataFrame): DataFrame with agent performance metrics
        date (str, optional): Date to generate report for (format: 'YYYY-MM-DD').
                             If None, uses the most recent date in the data.
    
    Returns:
        str: Formatted detailed report
    """
    try:
        logger.info("Generating detailed performance report")
        
        # If date is not provided, use the most recent date in the data
        if date is None:
            latest_date = metrics_df['call_date'].max()
            date_str = latest_date.strftime('%Y-%m-%d')
        else:
            # Parse the provided date
            date_str = date
            latest_date = pd.to_datetime(date)
        
        # Filter data for the specified date
        daily_data = metrics_df[metrics_df['call_date'] == latest_date].copy()
        
        if daily_data.empty:
            logger.warning(f"No data available for date: {date_str}")
            return f"Detailed Agent Performance Report for {date_str}\nNo data available for this date."
        
        # Sort by connect rate (descending)
        daily_data = daily_data.sort_values(by='connect_rate', ascending=False)
        
        # Format the report header
        report = f"Detailed Agent Performance Report for {date_str}\n"
        report += "=" * 50 + "\n\n"
        
        # Add summary statistics
        total_agents = daily_data.shape[0]
        total_active_agents = daily_data[daily_data['presence'] == 1].shape[0]
        total_calls = daily_data['total_calls'].sum()
        avg_connect_rate = (daily_data['completed_calls'].sum() / total_calls * 100).round(1)
        avg_call_duration = daily_data['avg_call_duration_minutes'].mean().round(1)
        
        report += f"Total Agents: {total_agents}\n"
        report += f"Active Agents: {total_active_agents}\n"
        report += f"Total Calls Made: {total_calls}\n"
        report += f"Average Connect Rate: {avg_connect_rate}%\n"
        report += f"Average Call Duration: {avg_call_duration} min\n\n"
        
        # Add top 5 performers
        report += "Top 5 Performers:\n"
        report += "-" * 50 + "\n"
        report += f"{'Agent Name':<20} {'Office':<15} {'Calls':<8} {'Connect Rate':<12} {'Avg Duration':<12}\n"
        report += "-" * 50 + "\n"
        
        for _, row in daily_data.head(5).iterrows():
            report += f"{row['agent_full_name']:<20} {row['users_office_location']:<15} "
            report += f"{row['total_calls']:<8} {row['connect_rate_percentage']:.1f}%{'':<6} "
            report += f"{row['avg_call_duration_minutes']:.1f} min\n"
        
        logger.info(f"Detailed report generated for {date_str}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating detailed report: {str(e)}")
        return f"Error generating detailed report: {str(e)}"