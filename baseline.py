import requests

# This is your LIVE Hugging Face App URL
BASE_URL = "https://eliab-data-privacy-agent-geu.hf.space"

def test_environment():
    print(f"🚀 Testing Environment at: {BASE_URL}")
    
    # Step 1: Reset the environment to get the 'Easy' task
    print("\n--- Step 1: Resetting ---")
    reset_payload = {"task_id": "mask-emails"}
    try:
        response = requests.post(f"{BASE_URL}/reset", json=reset_payload)
        data = response.json()
        print(f"Instruction: {data['observation']['instruction']}")
        print(f"Initial Data: {data['observation']['data']}")
        
        # Step 2: Take the 'mask' action
        print("\n--- Step 2: Taking Action ('mask') ---")
        action_payload = {"command": "mask", "target": "email"}
        step_response = requests.post(f"{BASE_URL}/step", json=action_payload)
        step_data = step_response.json()
        
        print(f"Reward Received: {step_data.get('reward')}")
        print(f"Processed Data: {step_data['observation']['data']}")
        
        if step_data.get('reward') == 1.0:
            print("\n✅ SUCCESS: The environment correctly graded the task!")
            
    except Exception as e:
        print(f"❌ Error connecting to Space: {e}")

if __name__ == "__main__":
    test_environment()
