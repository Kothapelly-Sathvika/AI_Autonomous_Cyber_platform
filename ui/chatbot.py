"""
AI Chatbot – cybersecurity knowledge assistant
"""
import streamlit as st

_KNOWLEDGE = {
    "phishing": (
        "**Phishing** is a social-engineering attack where an attacker sends a fraudulent "
        "message (email, SMS, etc.) designed to trick the victim into revealing sensitive "
        "information or clicking a malicious link.\n\n"
        "**Prevention:**\n"
        "- Train employees to recognise suspicious emails\n"
        "- Use email filtering and DMARC/SPF/DKIM\n"
        "- Enable MFA on all accounts\n"
        "- Never click links from unknown senders"
    ),
    "ransomware": (
        "**Ransomware** encrypts a victim's files and demands payment for the decryption key.\n\n"
        "**Prevention:**\n"
        "- Keep offline, tested backups\n"
        "- Patch operating systems and software promptly\n"
        "- Segment networks to limit lateral spread\n"
        "- Deploy EDR / anti-ransomware solutions\n"
        "- Disable unnecessary RDP access"
    ),
    "sql injection": (
        "**SQL Injection (SQLi)** injects malicious SQL code into application queries to "
        "manipulate or exfiltrate data.\n\n"
        "**Prevention:**\n"
        "- Use parameterised queries / prepared statements\n"
        "- Employ an ORM or stored procedures\n"
        "- Validate and sanitise all user inputs\n"
        "- Use a WAF (Web Application Firewall)"
    ),
    "ddos": (
        "**DDoS (Distributed Denial of Service)** overwhelms a target with traffic from "
        "many sources, rendering it unavailable.\n\n"
        "**Mitigation:**\n"
        "- Use a CDN or DDoS protection service (Cloudflare, AWS Shield)\n"
        "- Rate-limit incoming traffic\n"
        "- Deploy Anycast routing\n"
        "- Maintain excess bandwidth capacity"
    ),
    "brute force": (
        "**Brute Force** attacks systematically try all possible passwords or keys.\n\n"
        "**Prevention:**\n"
        "- Enforce strong password policies\n"
        "- Implement account lockout after failed attempts\n"
        "- Use CAPTCHA after repeated failures\n"
        "- Enable multi-factor authentication"
    ),
    "xss": (
        "**Cross-Site Scripting (XSS)** injects malicious scripts into web pages viewed "
        "by other users.\n\n"
        "**Prevention:**\n"
        "- Sanitise and encode all user output\n"
        "- Use Content Security Policy (CSP) headers\n"
        "- Validate inputs on both client and server\n"
        "- Use modern frameworks that auto-escape output"
    ),
    "malware": (
        "**Malware** is any malicious software (viruses, trojans, worms, spyware) designed "
        "to harm systems or steal data.\n\n"
        "**Prevention:**\n"
        "- Keep antivirus/anti-malware updated\n"
        "- Patch systems regularly\n"
        "- Restrict admin privileges\n"
        "- Use application whitelisting\n"
        "- Monitor network traffic for C2 communications"
    ),
    "secure network": (
        "**Securing your network** involves multiple layers:\n\n"
        "1. **Firewall:** Deploy and properly configure a next-gen firewall\n"
        "2. **Segmentation:** Separate critical assets into VLANs\n"
        "3. **IDS/IPS:** Deploy intrusion detection/prevention systems\n"
        "4. **Monitoring:** Implement 24/7 SIEM monitoring\n"
        "5. **Access Control:** Use least-privilege and NAC\n"
        "6. **Encryption:** Encrypt data in transit (TLS) and at rest\n"
        "7. **Patching:** Maintain a rigorous patch management cycle\n"
        "8. **Training:** Conduct regular security awareness training"
    ),
    "insider threat": (
        "**Insider Threat** comes from employees, contractors, or partners who misuse "
        "legitimate access.\n\n"
        "**Prevention:**\n"
        "- Implement least-privilege access\n"
        "- Monitor for anomalous data access patterns\n"
        "- Use DLP (Data Loss Prevention) tools\n"
        "- Conduct background checks\n"
        "- Establish a security-aware culture"
    ),
    "credential theft": (
        "**Credential Theft** involves stealing usernames/passwords via phishing, "
        "keyloggers, or credential-stuffing.\n\n"
        "**Prevention:**\n"
        "- Enforce MFA everywhere\n"
        "- Use password managers\n"
        "- Monitor for credential leaks on the dark web\n"
        "- Implement conditional access policies"
    ),
    "port scan": (
        "**Port Scanning** probes a host to discover open ports and services.\n\n"
        "**Prevention:**\n"
        "- Close unnecessary ports\n"
        "- Use firewall rules to block unauthorised scans\n"
        "- Deploy IDS to detect and alert on scan activity\n"
        "- Rate-limit connection attempts"
    ),
    "spam": (
        "**Spam** refers to bulk unsolicited messages sent to large numbers of users, "
        "often containing malicious links, malware attachments, or fraudulent offers.\n\n"
        "**Prevention:**\n"
        "- Deploy robust email filtering (SPF, DKIM, DMARC)\n"
        "- Use AI-powered spam detection to flag suspicious messages\n"
        "- Block known spam-sending IPs and domains\n"
        "- Train users to recognise and report spam\n"
        "- Never click links or open attachments from unknown senders"
    ),
}

_GREETINGS = [
    "Hello! I'm your AI Cybersecurity Assistant. Ask me about any cyber threat!",
    "I can explain phishing, ransomware, SQL Injection, DDoS, malware, and more.",
    "Try asking: *'How do I secure my network?'* or *'What is ransomware?'*",
]


def show_chatbot():
    st.markdown("## 🤖 AI Cybersecurity Assistant")
    st.markdown("---")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display history
    for role, text in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(text)

    # Suggestions
    st.markdown("#### 💡 Try asking:")
    suggestions = [
        "What is phishing?",
        "How to stop ransomware?",
        "Explain SQL Injection",
        "How do I secure my network?",
        "What is a DDoS attack?",
        "Tell me about insider threats",
    ]
    cols = st.columns(3)
    for i, sug in enumerate(suggestions):
        if cols[i % 3].button(sug, key=f"sug_{i}"):
            _process_question(sug)
            st.rerun()

    # Chat input
    user_input = st.chat_input("Ask a cybersecurity question…")
    if user_input:
        _process_question(user_input)
        st.rerun()


def _process_question(question: str):
    st.session_state["chat_history"].append(("user", question))
    q_lower = question.lower()

    answer = None
    for key, val in _KNOWLEDGE.items():
        if key in q_lower:
            answer = val
            break

    if not answer:
        answer = (
            "I don't have a specific answer for that question, but here are some "
            "general cybersecurity tips:\n\n"
            "- Keep all software and systems patched\n"
            "- Use strong, unique passwords with MFA\n"
            "- Regularly backup critical data\n"
            "- Train staff on security awareness\n"
            "- Monitor logs and network traffic\n"
            "- Follow the principle of least privilege\n\n"
            "Try asking about: phishing, ransomware, SQL injection, DDoS, malware, "
            "XSS, brute force, insider threats, credential theft, port scanning, "
            "or network security."
        )

    st.session_state["chat_history"].append(("assistant", answer))
