import streamlit as st

# Simulated state (in real app, replace with actual checks)
api_status = st.session_state.get("api_status", "DOWN")  # Could be 'UP' or 'DOWN'
show_api_info = st.session_state.get("show_api_info", False)
queue = st.session_state.get("queue", [])

st.set_page_config(page_title="Real-Time Traffic & Weather API", page_icon="🚦", layout="wide")

# Main Header
st.markdown("<h1 style='text-align: center;'>🚦 Real-Time Traffic & Weather API</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Monitor live API status and reserve access for tomorrow (if API is down)</p>", unsafe_allow_html=True)
st.write("")

# Initial Form
if not show_api_info:
    with st.form("user_info_form"):
        st.subheader("🚪 Knock knock...")
        st.write("Before jumping into the app, I'd love to know a bit about who's visiting. Helps me improve and connect. 🚀")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name", placeholder="e.g. John Doe", max_chars=50)
        with col2:
            contact = st.text_input("Email or LinkedIn (optional)", placeholder="e.g. john@example.com")

        col3, col4 = st.columns(2)
        with col3:
            role = st.selectbox("You're here as a...", ["Recruiter", "Developer", "Friend", "Just Curious 👀", "Other"])
        with col4:
            purpose = st.selectbox("What brings you here?", ["Hiring", "Checking out portfolio", "Collaboration", "Giving Feedback", "Other"])

        message = st.text_area("Anything you'd like to share? (Optional)", placeholder="Your message here...")

        submitted = st.form_submit_button("Submit")
        skipped = st.form_submit_button("Skip for now")

        if submitted or skipped:
            st.session_state.show_api_info = True
            st.experimental_rerun()

else:
    if api_status == "DOWN":
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🔢 Priority Queue for Tomorrow")
            if queue:
                st.markdown("#### Reserved Users")
                st.markdown("\n".join([f"{i+1}. {user}" for i, user in enumerate(queue)]))
            else:
                st.info("No users have reserved access yet.")

        with col2:
            st.subheader("🛰 API Status:")
            st.error("🚨 Oops! The API is currently unavailable.")
            st.markdown("""
            This project runs on a free-tier API with limited daily requests (2,500 max).  
            Today’s quota has been used up or the system marked it as temporarily down due to health checks.

            ⏳ **Good news:** You can **reserve your access for tomorrow** right now to get early access when the system is back!
            """)
            with st.form("reserve_form"):
                username = st.text_input("Create a unique username", placeholder="e.g. your_custom_id")
                reserve_submit = st.form_submit_button("Reserve API Access for Tomorrow")

                if reserve_submit:
                    if username in queue:
                        st.warning("🚫 Username already reserved. Try a different one.")
                    elif username.strip() == "":
                        st.warning("Please enter a username.")
                    else:
                        queue.append(username)
                        st.session_state.queue = queue
                        st.success(f"✅ Reserved successfully as **{username}**")
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🐳 Docker Access Now Live!")
            st.success("The API is online and ready for action.")
            st.markdown("#### Pull the image and get started:")
            st.code("docker pull animesh/api-traffic-weather:latest", language="bash")
            st.info("Containers don’t wait — and neither should you!")

        with col2:
            st.subheader("🛰 API Status:")
            st.success("✅ The API is live and healthy. You're good to go!")
            st.write("Use it while it lasts 😅")
            st.markdown("---")
            st.warning("⚠️ Heads-up: This is a free-tier project, so API calls are limited.")
            st.markdown("When the quota hits the fan, you’ll see the “Reserve for Tomorrow” screen again.")
            st.markdown("Until then — **code away 🚀** and may your requests be fast and your rate limits merciful.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ by <strong>Animesh</strong></p>", unsafe_allow_html=True)
