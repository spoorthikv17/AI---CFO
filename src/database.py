import streamlit as st


st.set_page_config(
    page_title="AI CFO",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fc;
    }

    .auth-container {
        max-width: 520px;
        margin: 70px auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.08);
    }

    .brand {
        text-align: center;
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .tagline {
        text-align: center;
        color: #6b7280;
        margin-bottom: 30px;
    }

    .welcome {
        text-align: center;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# LOGIN / SIGNUP
# --------------------------------------------------

if not st.session_state.authenticated:

    st.markdown(
        '<div class="auth-container">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand">💰 AI CFO</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tagline">'
        'Your intelligent financial assistant'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.auth_page == "login":

        st.markdown(
            '<div class="welcome">'
            '<h2>Welcome back 👋</h2>'
            '<p>Login to continue to your AI CFO</p>'
            '</div>',
            unsafe_allow_html=True
        )

        login_id = st.text_input(
            "Email or Phone",
            placeholder="Enter your email or phone number"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):
            if login_id and password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(
                    "Please enter your email/phone and password."
                )

        st.divider()

        if st.button(
            "Forgot Password?",
            use_container_width=True
        ):
            st.info(
                "Password recovery will be connected "
                "when we build the authentication backend."
            )

        if st.button(
            "Create New Account",
            use_container_width=True
        ):
            st.session_state.auth_page = "signup"
            st.rerun()

    else:

        st.markdown(
            '<div class="welcome">'
            '<h2>Create your account 🚀</h2>'
            '<p>Start managing your finances intelligently</p>'
            '</div>',
            unsafe_allow_html=True
        )

        name = st.text_input(
            "Full Name",
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter your phone number"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):
            if not all(
                [
                    name,
                    email,
                    phone,
                    password,
                    confirm_password
                ]
            ):
                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            else:
                st.success(
                    "Account UI is ready. "
                    "Real authentication will be connected next."
                )

        st.divider()

        if st.button(
            "Already have an account? Login",
            use_container_width=True
        ):
            st.session_state.auth_page = "login"
            st.rerun()

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.stop()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.sidebar.title("💰 AI CFO")

st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Overview",
        "💳 Transactions",
        "🧾 Receipts",
        "📊 Analytics",
        "🔮 Forecast",
        "⚠️ Risk & Anomalies",
        "🤖 AI CFO",
        "⚙️ Settings"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):
    st.session_state.authenticated = False
    st.session_state.auth_page = "login"
    st.rerun()


st.title("🏠 AI CFO Dashboard")

st.write(
    "Welcome to your financial command center."
)

st.info(
    "Dashboard modules will be connected to your real "
    "financial database step by step."
)