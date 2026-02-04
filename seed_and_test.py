import sys
import os
import requests
from sqlalchemy import text
from app.db.session import SessionLocal

# Add current dir to path
sys.path.append(os.getcwd())

API_URL = "http://127.0.0.1:8000"

def get_otp(email):
    db = SessionLocal()
    try:
        # Fetch the latest OTP for this email
        result = db.execute(text(f"SELECT otp_code FROM email_otps WHERE email = '{email}' ORDER BY created_at DESC LIMIT 1"))
        return result.scalar()
    finally:
        db.close()

def register_flow(username, email, password, full_name):
    print(f"\n[Process] Registering {username}...")
    
    # 1. Register
    resp = requests.post(f"{API_URL}/auth/register", json={"username": username, "email": email, "password": password, "full_name": full_name})
    if resp.status_code != 200:
        # Handle case if user already exists (for re-runs)
        if "already exists" in resp.text:
             print(f"  -> User {username} likely exists. Attempting login...")
             pass 
        else:
            print(f"FAILED to register {username}: {resp.text}")
            return None
    
    # 2. Verify User Directly (Bypass OTP for Test)
    # otp = get_otp(email)
    # print(f"  -> OTP Fetched from DB: {otp}")
    
    # Direct DB Update
    db = SessionLocal()
    try:
        db.execute(text(f"UPDATE users SET is_email_verified = true WHERE email = '{email}'"))
        db.commit()
        print(f"  -> Manually set is_email_verified=True for {email}")
    except Exception as e:
        print(f"  -> DB Update Failed: {e}")
    finally:
        db.close()

    # 3. Skip API OTP verification and go to Login
    print("  -> Skipped OTP API verification (using direct DB update).")
    
    # 4. Login
    resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"FAILED to login: {resp.text}")
        return None
    
    token = resp.json()["access_token"]
    print("  -> Logged In.")
    return token

def main():
    print("=== STARTING END-TO-END TEST ===")
    
    # --- 1. Create Bot Users ---
    bot1_token = register_flow("bot_alpha", "bot.alpha@example.com", "botpass123", "Alpha Bot")
    bot2_token = register_flow("bot_beta", "bot.beta@example.com", "botpass123", "Beta Bot")
    
    headers_bot1 = {"Authorization": f"Bearer {bot1_token}"}
    headers_bot2 = {"Authorization": f"Bearer {bot2_token}"}

    # --- 2. Bots Create Posts ---
    print("\n[Action] Bots creating posts...")
    requests.post(f"{API_URL}/social/", headers=headers_bot1, json={"content_text": "Hello form Alpha!", "caption": "First post"})
    requests.post(f"{API_URL}/social/", headers=headers_bot1, json={"content_text": "Alpha updates...", "caption": "Second post"})
    requests.post(f"{API_URL}/social/", headers=headers_bot2, json={"content_text": "Beta is here!", "caption": "Beta post"})
    print("  -> Posts created.")

    # --- 3. Create Main User ---
    main_email = "241574109@formanite.fccollege.edu.pk" # As requested
    main_token = register_flow("main_user_wajih", main_email, "securepass", "Wajih Test")
    headers_main = {"Authorization": f"Bearer {main_token}"}
    
    # --- 4. Main User Follows Bots ---
    print("\n[Action] Main user following bots...")
    # Need IDs first. Let's look up public profile
    bot1_id = requests.get(f"{API_URL}/users/bot_alpha", headers=headers_main).json()["id"]
    bot2_id = requests.get(f"{API_URL}/users/bot_beta", headers=headers_main).json()["id"]
    
    requests.post(f"{API_URL}/social/{bot1_id}/follow", headers=headers_main)
    requests.post(f"{API_URL}/social/{bot2_id}/follow", headers=headers_main)
    print("  -> Followed Bot Alpha and Bot Beta.")

    # --- 5. Verify Feed ---
    print("\n[Verification] Checking Main User Feed...")
    feed_resp = requests.get(f"{API_URL}/social/feed", headers=headers_main)
    posts = feed_resp.json()
    print(f"  -> Feed contains {len(posts)} posts. (Expected at least 3)")
    for p in posts:
        print(f"     - [{p['owner']['username']}] {p['content_text']} (Caption: {p.get('caption')})")

    # --- 6. Bot Follows Main User (Notification Test) ---
    print("\n[Action] Bot Alpha following Main User...")
    # Get main user ID
    main_user_id = requests.get(f"{API_URL}/users/me", headers=headers_main).json()["id"]
    requests.post(f"{API_URL}/social/{main_user_id}/follow", headers=headers_bot1)
    
    # --- 7. Verify Notification ---
    print("\n[Verification] Checking Main User Notifications...")
    notif_resp = requests.get(f"{API_URL}/notifications/", headers=headers_main)
    if notif_resp.status_code != 200:
        print(f"FAILED to get notifications: {notif_resp.status_code} {notif_resp.text}")
    else:
        notifs = notif_resp.json()
        print(f"  -> Found {len(notifs)} notifications.")
        for n in notifs:
            try:
                print(f"     - [Type: {n.get('type')}] From: {n.get('sender', {}).get('username')}")
            except Exception as e:
                print(f"     - Error parsing notif: {n} ({e})")

if __name__ == "__main__":
    main()
