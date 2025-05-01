"""
Functions for data ingestion from CSV files.
Handles reading CSVs and initial data type conversions.
"""
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_csv_file(file_path):
    """
    Read a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing the CSV data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
        pd.errors.ParserError: If there's an error parsing the CSV
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        
        if df.empty:
            logger.warning(f"Empty file: {file_path}")
            
        logger.info(f"Successfully read {len(df)} rows from {file_path}")
        return df
        
    except pd.errors.EmptyDataError:
        logger.error(f"Empty file: {file_path}")
        raise
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {str(e)}")
        raise

def read_call_logs(file_path):
    """
    Read and process call logs data.
    
    Args:
        file_path (str): Path to the call_logs.csv file
        
    Returns:
        pd.DataFrame: Processed call logs DataFrame
    """
    df = read_csv_file(file_path)
    
    # Convert date and timestamp columns to datetime
    try:
        if 'created_ts' in df.columns:
            df['created_ts'] = pd.to_datetime(df['created_ts'])
            
        if 'call_date' in df.columns:
            df['call_date'] = pd.to_datetime(df['call_date'])
            
        # Convert duration to numeric
        if 'duration' in df.columns:
            df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
            
        # Convert ID columns to string for proper joining
        for col in ['call_id', 'agent_id', 'org_id', 'installment_id']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                
        logger.info("Call logs data processed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error processing call logs data: {str(e)}")
        raise

def read_agent_roster(file_path):
    """
    Read and process agent roster data.
    
    Args:
        file_path (str): Path to the agent_roster.csv file
        
    Returns:
        pd.DataFrame: Processed agent roster DataFrame
    """
    df = read_csv_file(file_path)
    
    try:
        # Convert ID columns to string for proper joining
        for col in ['agent_id', 'org_id']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                
        logger.info("Agent roster data processed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error processing agent roster data: {str(e)}")
        raise

def read_disposition_summary(file_path):
    """
    Read and process disposition summary data.
    
    Args:
        file_path (str): Path to the disposition_summary.csv file
        
    Returns:
        pd.DataFrame: Processed disposition summary DataFrame
    """
    df = read_csv_file(file_path)
    
    try:
        # Convert date and time columns to datetime
        if 'call_date' in df.columns:
            df['call_date'] = pd.to_datetime(df['call_date'])
            
        if 'login_time' in df.columns:
            df['login_time'] = pd.to_datetime(df['login_time'], errors='coerce')
            
        # Convert ID columns to string for proper joining
        for col in ['agent_id', 'org_id']:
            if col in df.columns:
                df[col] = df[col].astype(str)
                
        logger.info("Disposition summary data processed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error processing disposition summary data: {str(e)}")
        raise