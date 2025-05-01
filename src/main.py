"""
Main entry point for the DPDzero Data Ops Assignment.
Orchestrates the entire data pipeline.
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# Add the parent directory to sys.path to allow importing the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import read_call_logs, read_agent_roster, read_disposition_summary
from src.validation import validate_call_logs, validate_agent_roster, validate_disposition_summary
from src.processing import merge_call_logs_with_agent_roster, merge_with_disposition_summary, calculate_performance_metrics
from src.reporting import save_performance_summary, generate_slack_summary, generate_detailed_report

def setup_logging(log_dir="logs"):
    """
    Set up logging configuration.
    
    Args:
        log_dir (str): Directory to store log files
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"pipeline_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="DPDzero Data Pipeline")
    
    parser.add_argument(
        "--call-logs",
        type=str,
        default="data/call_logs.csv",
        help="Path to call logs CSV file (default: data/call_logs.csv)"
    )
    
    parser.add_argument(
        "--agent-roster",
        type=str,
        default="data/agent_roster.csv",
        help="Path to agent roster CSV file (default: data/agent_roster.csv)"
    )
    
    parser.add_argument(
        "--disposition-summary",
        type=str,
        default="data/disposition_summary.csv",
        help="Path to disposition summary CSV file (default: data/disposition_summary.csv)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="agent_performance_summary.csv",
        help="Path to output CSV file (default: agent_performance_summary.csv)"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to generate report for (format: YYYY-MM-DD). If not provided, uses the most recent date."
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate a detailed report in addition to the Slack summary"
    )
    
    return parser.parse_args()

def main():
    """
    Main function to run the data pipeline.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging()
    logger.info("Starting DPDzero Data Pipeline")
    
    try:
        # Step 1: Data Ingestion
        logger.info("Step 1: Data Ingestion")
        
        call_logs_df = read_call_logs(args.call_logs)
        agent_roster_df = read_agent_roster(args.agent_roster)
        disposition_df = read_disposition_summary(args.disposition_summary)
        
        # Step 2: Data Validation
        logger.info("Step 2: Data Validation")
        
        call_logs_validated = validate_call_logs(call_logs_df)
        agent_roster_validated = validate_agent_roster(agent_roster_df)
        disposition_validated = validate_disposition_summary(disposition_df)
        
        # Step 3: Data Processing and Feature Engineering
        logger.info("Step 3: Data Processing and Feature Engineering")
        
        # Merge call logs with agent roster
        merged_df = merge_call_logs_with_agent_roster(call_logs_validated, agent_roster_validated)
        
        # Merge with disposition summary
        final_df = merge_with_disposition_summary(merged_df, disposition_validated)
        
        # Calculate performance metrics
        metrics_df = calculate_performance_metrics(final_df)
        
        # Step 4: Reporting
        logger.info("Step 4: Reporting")
        
        # Save performance summary to CSV
        save_performance_summary(metrics_df, args.output)
        
        # Generate and display Slack summary
        slack_summary = generate_slack_summary(metrics_df, args.date)
        print("\n" + slack_summary + "\n")
        
        # Generate detailed report if requested
        if args.detailed:
            detailed_report = generate_detailed_report(metrics_df, args.date)
            print("\n" + detailed_report + "\n")
        
        logger.info("Data pipeline completed successfully")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())