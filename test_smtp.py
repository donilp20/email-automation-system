import smtplib
import ssl

def test_gmail_smtp():
    """Quick test of Gmail SMTP connection"""
    
    # CREDENTIALS
    email = "donilpatel2003@gmail.com"
    app_password = "puzc yhfx stci pgsp"
    
    print("=" * 60)
    print("🔍 Testing Gmail SMTP Connection")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"App Password Length: {len(app_password)}")
    print("=" * 60)
    
    try:
        print("\n Creating SSL context...")
        context = ssl.create_default_context()
        
        print(" Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        print(" Connected!")
        
        print(" Starting TLS...")
        server.starttls(context=context)
        print("TLS started!")
        
        print(" Logging in...")
        server.login(email, app_password)
        print("Login successful!")
        
        server.quit()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Gmail SMTP is working perfectly!")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n Authentication failed: {e}")
        print("\n Troubleshooting:")
        print("   1. Generate new app password at:")
        print("      https://myaccount.google.com/apppasswords")
        print("   2. Make sure 2FA is enabled")
        print("   3. Copy password exactly (no spaces)")
        return False
        
    except Exception as e:
        print(f"\n Connection failed: {e}")
        print("\n This could be:")
        print("   - Network/firewall issue")
        print("   - Docker network configuration")
        print("   - Port 587 blocked")
        return False

if __name__ == "__main__":
    test_gmail_smtp()
