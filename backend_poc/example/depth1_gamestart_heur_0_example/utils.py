import time
import math

def format_time(nanoseconds):
    """Converts nanoseconds into an intelligent time format (minutes, seconds, milliseconds, nanoseconds)."""
    # Constants
    MINUTE = 60 * 1_000_000_000  # 1 minute in nanoseconds
    SECOND = 1_000_000_000       # 1 second in nanoseconds
    MILLISECOND = 1_000_000      # 1 millisecond in nanoseconds
    
    if nanoseconds >= MINUTE:
        # Convert to minutes and round up
        minutes = math.ceil(nanoseconds / MINUTE)
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    elif nanoseconds >= SECOND:
        # Convert to seconds and round up
        seconds = math.ceil(nanoseconds / SECOND)
        return f"{seconds} second{'s' if seconds > 1 else ''}"
    
    elif nanoseconds >= MILLISECOND:
        # Convert to milliseconds and round up
        milliseconds = math.ceil(nanoseconds / MILLISECOND)
        return f"{milliseconds} millisecond{'s' if milliseconds > 1 else ''}"
    
    else:
        # Return the value in nanoseconds if it's too small
        return f"{nanoseconds} nanosecond{'s' if nanoseconds > 1 else ''}"

def measure_duration_ns(func):
    """Decorator to measure the duration of a function in nanoseconds and print it in a human-readable format."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start timing
        result = func(*args, **kwargs)     # Call the function
        end_time = time.perf_counter()      # End timing
        duration_ns = (end_time - start_time) * 1_000_000_000  # Convert to nanoseconds
        
        # Format the duration intelligently
        formatted_duration = format_time(duration_ns)
        
        # Print the result
        print(f"Function '{func.__name__}' took {formatted_duration}")
        
        return result
    
    return wrapper

def pretty_print_board(buffer, BOARD_SIZE):
	counter = 0
	for byte in buffer:
		print(f" {int(byte)} ", end='')
		counter += 1
		if counter == BOARD_SIZE:
			print("")
			counter = 0

def pretty_print_board_indent(buffer, BOARD_SIZE, indent_count):
	counter = 0
	print(" " * indent_count * 2, end='')
	for byte in buffer:
		print(f" {int(byte)} ", end='')
		counter += 1
		if counter == BOARD_SIZE:
			print("")
			print(" " * indent_count * 2, end='')
			counter = 0

def get_top_idx(idx, BOARD_SIZE):
	if idx < BOARD_SIZE:
		return -1
	return idx - BOARD_SIZE

def get_btm_idx(idx, BOARD_SIZE):
	dim = (BOARD_SIZE * BOARD_SIZE)
	if idx > (dim - BOARD_SIZE - 1):
		return -1
	return idx + BOARD_SIZE

def get_left_idx(idx, BOARD_SIZE):
	if (idx) % BOARD_SIZE == 0:
		return -1
	return idx - 1

def get_right_idx(idx, BOARD_SIZE):
	if (idx + 1) % BOARD_SIZE == 0:
		return -1
	return idx + 1

def get_top_left_idx(idx, BOARD_SIZE):
	top = get_top_idx(idx, BOARD_SIZE)
	if top == -1:
		return -1
	return get_left_idx(top, BOARD_SIZE)

def get_btm_left_idx(idx, BOARD_SIZE):
	btm = get_btm_idx(idx, BOARD_SIZE)
	if btm == -1:
		return -1
	return get_left_idx(btm, BOARD_SIZE)

def get_top_right_idx(idx, BOARD_SIZE):
	top = get_top_idx(idx, BOARD_SIZE)
	if top == -1:
		return -1
	return get_right_idx(top, BOARD_SIZE)

def get_btm_right_idx(idx, BOARD_SIZE):
	btm = get_btm_idx(idx, BOARD_SIZE)
	if btm == -1:
		return -1
	return get_right_idx(btm, BOARD_SIZE)