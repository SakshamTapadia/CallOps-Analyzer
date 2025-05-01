"""
Functions for data validation, including checking for required columns,
validating data types, and identifying missing or duplicate data.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def validate_required_columns(df, required_columns, file_name):
    """
    Check if all required columns exist in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list): List of required column names
        file_name (str): Name of the file for logging purposes
        
    Returns:
        bool: True if all required columns exist, False otherwise
        
    Raises:
        ValueError: If any required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        error_msg = f"Missing required columns in {file_name}: {missing_columns}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"All required columns present in {file_name}")
    return True

def check_for_duplicates(df, subset_columns, file_name):
    """
    Check for duplicate rows in the DataFrame based on specific columns.
    
    Args:
        df (pd.DataFrame): DataFrame to check
        subset_columns (list): List of columns to consider for duplicates
        file_name (str): Name of the file for logging purposes
        
    Returns:
        pd.DataFrame: DataFrame with duplicates removed
    """
    # Check for duplicates
    duplicates = df.duplicated(subset=subset_columns, keep='first')
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        logger.warning(f"Found {duplicate_count} duplicate rows in {file_name}")
        
        # Get indices of duplicates for logging
        duplicate_indices = np.where(duplicates)[0]
        if len(duplicate_indices) > 0:
            sample_duplicate = df.iloc[duplicate_indices[0]]
            logger.debug(f"Sample duplicate: {sample_duplicate.to_dict()}")
        
        # Remove duplicates
        df_deduped = df.drop_duplicates(subset=subset_columns, keep='first')
        logger.info(f"Removed {duplicate_count} duplicates from {file_name}")
        return df_deduped
    else:
        logger.info(f"No duplicates found in {file_name}")
        return df

def check_missing_values(df, file_name):
    """
    Check for missing values in all columns of the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to check
        file_name (str): Name of the file for logging purposes
        
    Returns:
        dict: Dictionary with column names as keys and number of missing values as values
    """
    missing_values = df.isnull().sum().to_dict()
    missing_columns = {col: count for col, count in missing_values.items() if count > 0}
    
    if missing_columns:
        for col, count in missing_columns.items():
            percentage = (count / len(df)) * 100
            logger.warning(f"{file_name}: Column '{col}' has {count} missing values ({percentage:.2f}%)")
    else:
        logger.info(f"No missing values found in {file_name}")
    
    return missing_values

def validate_id_formats(df, id_columns, file_name):
    """
    Validate that ID columns contain valid values.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        id_columns (list): List of ID column names
        file_name (str): Name of the file for logging purposes
        
    Returns:
        pd.DataFrame: DataFrame with validated and fixed IDs
    """
    df_copy = df.copy()
    
    for col in id_columns:
        if col in df.columns:
            # Check for missing IDs
            missing_ids = df[col].isnull().sum()
            if missing_ids > 0:
                logger.warning(f"{file_name}: {missing_ids} missing values in '{col}'")
            
            # Convert to string to ensure proper joining
            df_copy[col] = df_copy[col].astype(str)
            
            # Replace 'nan' strings from null values with empty strings for better handling
            df_copy[col] = df_copy[col].replace('nan', '')
    
    return df_copy

def validate_date_formats(df, date_columns, file_name):
    """
    Validate that date columns contain valid dates.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        date_columns (list): List of date column names
        file_name (str): Name of the file for logging purposes
        
    Returns:
        pd.DataFrame: DataFrame with validated dates
    """
    df_copy = df.copy()
    
    for col in date_columns:
        if col in df.columns:
            # Try to convert to datetime, note errors
            try:
                # Store original values
                original_values = df_copy[col].copy()
                
                # Convert to datetime
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                
                # Count NaT values (Not a Time) that weren't NaN before
                invalid_dates = ((df_copy[col].isnull()) & (~original_values.isnull())).sum()
                
                if invalid_dates > 0:
                    logger.warning(f"{file_name}: {invalid_dates} invalid date values in '{col}'")
                
            except Exception as e:
                logger.error(f"Error validating dates in {file_name}, column '{col}': {str(e)}")
    
    return df_copy

def validate_call_logs(df):
    """
    Validate call logs DataFrame.
    
    Args:
        df (pd.DataFrame): Call logs DataFrame
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    file_name = "call_logs.csv"
    
    # Check required columns
    required_cols = ['call_id', 'agent_id', 'org_id', 'installment_id', 'status', 'duration', 'call_date']
    validate_required_columns(df, required_cols, file_name)
    
    # Check for duplicates based on call_id (should be unique)
    df = check_for_duplicates(df, ['call_id'], file_name)
    
    # Check for missing values
    check_missing_values(df, file_name)
    
    # Validate ID formats
    df = validate_id_formats(df, ['call_id', 'agent_id', 'org_id', 'installment_id'], file_name)
    
    # Validate date formats
    df = validate_date_formats(df, ['call_date', 'created_ts'], file_name)
    
    # Validate status values
    valid_statuses = ['completed', 'connected', 'failed', 'missed', 'busy', 'no-answer']
    invalid_statuses = df[~df['status'].isin(valid_statuses) & ~df['status'].isnull()]
    
    if len(invalid_statuses) > 0:
        logger.warning(f"Found {len(invalid_statuses)} records with invalid status values")
        logger.debug(f"Sample invalid statuses: {invalid_statuses['status'].unique()[:5]}")
    
    # Validate duration values (should be numeric and non-negative)
    if 'duration' in df.columns:
        try:
            df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
            negative_durations = (df['duration'] < 0).sum()
            
            if negative_durations > 0:
                logger.warning(f"Found {negative_durations} records with negative duration values")
                
        except Exception as e:
            logger.error(f"Error validating duration values: {str(e)}")
    
    return df

def validate_agent_roster(df):
    """
    Validate agent roster DataFrame.
    
    Args:
        df (pd.DataFrame): Agent roster DataFrame
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    file_name = "agent_roster.csv"
    
    # Check required columns
    required_cols = ['agent_id', 'users_first_name', 'users_last_name', 'users_office_location', 'org_id']
    validate_required_columns(df, required_cols, file_name)
    
    # Check for duplicates based on agent_id (should be unique)
    df = check_for_duplicates(df, ['agent_id'], file_name)
    
    # Check for missing values
    check_missing_values(df, file_name)
    
    # Validate ID formats
    df = validate_id_formats(df, ['agent_id', 'org_id'], file_name)
    
    return df

def validate_disposition_summary(df):
    """
    Validate disposition summary DataFrame.
    
    Args:
        df (pd.DataFrame): Disposition summary DataFrame
        
    Returns:
        pd.DataFrame: Validated DataFrame
    """
    file_name = "disposition_summary.csv"
    
    # Check required columns
    required_cols = ['agent_id', 'org_id', 'call_date', 'login_time']
    validate_required_columns(df, required_cols, file_name)
    
    # Check for duplicates based on agent_id, org_id, and call_date (should be unique per day per agent)
    df = check_for_duplicates(df, ['agent_id', 'org_id', 'call_date'], file_name)
    
    # Check for missing values
    check_missing_values(df, file_name)
    
    # Validate ID formats
    df = validate_id_formats(df, ['agent_id', 'org_id'], file_name)
    
    # Validate date formats
    df = validate_date_formats(df, ['call_date', 'login_time'], file_name)
    
    return df