"""Read the existing shared Anthropic accounts; never creates or resets policy."""
import json
from investigator.shared_state import configured_state
from investigator.anthropic_credit import status

def main():
 state=configured_state()
 if state is None:raise ValueError('AUTHORITATIVE_SHARED_STATE_REQUIRED')
 print(json.dumps(status(state),indent=2,default=str))
if __name__=='__main__':main()
