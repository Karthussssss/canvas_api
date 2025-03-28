import datetime

# Global variable to store the current update batch identifier
CURRENT_UPDATE_BATCH = None

def generate_batch_id():
    """Generate a unique batch identifier in the format YYMMDD-HHMM"""
    now = datetime.datetime.now()
    batch_id = now.strftime("%y%m%d-%H%M")
    return batch_id

def initialize_batch():
    """Initialize the batch identifier for the current run"""
    global CURRENT_UPDATE_BATCH
    CURRENT_UPDATE_BATCH = generate_batch_id()
    return CURRENT_UPDATE_BATCH

def get_current_batch():
    """Get the current batch identifier"""
    global CURRENT_UPDATE_BATCH
    # If not yet initialized, initialize it
    if CURRENT_UPDATE_BATCH is None:
        initialize_batch()
    return CURRENT_UPDATE_BATCH 