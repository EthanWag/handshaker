from handshake.applier import applier
from mcp.server.fastmcp import FastMCP
import os
import sys
from pathlib import Path
 
mcp = FastMCP("Applier")
 
# Define allowed directories for writing
ALLOWED_WRITE_DIRS = [
    os.path.expanduser("~/Personal-Projects/data"),
]
 
def is_write_allowed(filepath: str) -> bool:
    """Check if filepath is in allowed directories"""
    try:
        abs_path = os.path.abspath(filepath)
        return any(abs_path.startswith(os.path.abspath(d)) for d in ALLOWED_WRITE_DIRS)
    except Exception as e:
        print(f"Error checking write permissions: {e}", file=sys.stderr)
        return False
 
@mcp.tool()
async def handshake_applier(job_title: str, request_count: int = None) -> str:
    """Apply to Handshake jobs with error handling"""
    try:
        # Validate inputs
        if not job_title or not isinstance(job_title, str):
            raise ValueError("job_title must be a non-empty string")
        
        if request_count is not None and request_count <= 0:
            raise ValueError("request_count must be a positive integer")
        
        print(f"Starting applications for: {job_title} (count: {request_count})", file=sys.stderr)
        
        # Ensure output directory exists
        output_dir = os.path.expanduser("~/Personal-Projects/data")
        os.makedirs(output_dir, exist_ok=True)
        
        # Call applier with error context
        result = await applier(job_title=job_title, count=request_count)
        
        success_msg = f"Successfully applied to {request_count or 'all'} {job_title} roles"
        print(success_msg, file=sys.stderr)
        return success_msg
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except PermissionError as e:
        error_msg = f"Permission denied: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except FileNotFoundError as e:
        error_msg = f"File not found: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except Exception as e:
        error_msg = f"Unexpected error applying to jobs: {type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
 
@mcp.tool()
async def write_file(filepath: str, content: str) -> str:
    """Write content to a file (with permission checks and error handling)"""
    try:
        # Validate inputs
        if not filepath or not isinstance(filepath, str):
            raise ValueError("filepath must be a non-empty string")
        
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        
        # Check permissions
        if not is_write_allowed(filepath):
            raise PermissionError(f"Writing to {filepath} not allowed. Allowed dirs: {ALLOWED_WRITE_DIRS}")
        
        # Create directory if it doesn't exist
        try:
            dir_path = os.path.dirname(filepath)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            raise PermissionError(f"Cannot create directory {dir_path}: {str(e)}")
        
        # Write file
        try:
            with open(filepath, 'w') as f:
                f.write(content)
        except IOError as e:
            raise PermissionError(f"Cannot write to file {filepath}: {str(e)}")
        
        success_msg = f"Successfully wrote to {filepath}"
        print(success_msg, file=sys.stderr)
        return success_msg
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except PermissionError as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except Exception as e:
        error_msg = f"Unexpected error writing file: {type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
 
@mcp.tool()
async def read_file(filepath: str) -> str:
    """Read content from a file with error handling"""
    try:
        # Validate input
        if not filepath or not isinstance(filepath, str):
            raise ValueError("filepath must be a non-empty string")
        
        # Check permissions
        if not is_write_allowed(filepath):
            raise PermissionError(f"Reading from {filepath} not allowed. Allowed dirs: {ALLOWED_WRITE_DIRS}")
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File does not exist: {filepath}")
        
        # Read file
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except IOError as e:
            raise PermissionError(f"Cannot read file {filepath}: {str(e)}")
        
        print(f"Successfully read {filepath}", file=sys.stderr)
        return content
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except PermissionError as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
    
    except Exception as e:
        error_msg = f"Unexpected error reading file: {type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return f"Error: {error_msg}"
 
if __name__ == "__main__":
    print("Starting Applier MCP server...", file=sys.stderr)
    print(f"Allowed write directories: {ALLOWED_WRITE_DIRS}", file=sys.stderr)
    mcp.run()