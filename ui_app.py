import streamlit as st
import httpx

# -----------------------------
# Configuration
# -----------------------------

API_URL = "http://127.0.0.1:8002"

st.set_page_config(
    page_title="Scholarship Eligibility AI",
    page_icon="🎓"
)

st.title("🎓 Explainable Decision Intelligence System")
st.markdown(
    "Check your eligibility for Govt. Scholarships with detailed AI explanations."
)

# -----------------------------
# Sidebar Inputs
# -----------------------------

st.sidebar.header("Applicant Profile")

ruleset_id = st.sidebar.text_input(
    "Ruleset ID",
    value="scholarship_delhi_v1"
)

with st.sidebar.form("input_form"):

    st.subheader("Personal Details")

    income = st.number_input(
        "Annual Family Income (INR)",
        min_value=0,
        value=650000,
        step=10000
    )

    state = st.selectbox(
        "State of Residence",
        ["Delhi", "Haryana", "UP", "Other"]
    )

    age = st.number_input(
        "Age (Years)",
        min_value=10,
        max_value=100,
        value=19
    )

    category = st.selectbox(
        "Category",
        ["General", "SC", "ST", "OBC", "EWS"]
    )

    st.subheader("Academic Details")

    course_level = st.selectbox(
        "Course Level",
        ["Undergraduate", "Diploma", "Postgraduate", "Other"]
    )

    last_exam_percentage = st.number_input(
        "Last Exam Percentage",
        min_value=0.0,
        max_value=100.0,
        value=75.0
    )

    institute_state = st.selectbox(
        "Institute State",
        ["Delhi", "Haryana", "UP", "Other"]
    )

    st.subheader("Other Criteria")

    has_other_major_scholarship = st.checkbox(
        "Receiving other major scholarship?",
        value=False
    )

    is_first_generation_learner = st.checkbox(
        "First-generation learner?",
        value=False
    )

    submitted = st.form_submit_button("Check Eligibility")

# -----------------------------
# Logic
# -----------------------------

if submitted:

    payload = {
        "ruleset_id": ruleset_id,
        "user_input": {
            "income": int(income),
            "state": state,
            "age": int(age),
            "category": category,
            "course_level": course_level,
            "last_exam_percentage": last_exam_percentage,
            "institute_state": institute_state,
            "has_other_major_scholarship": has_other_major_scholarship,
            "is_first_generation_learner": is_first_generation_learner
        }
    }

    with st.spinner("Analyzing eligibility against rules..."):

        try:
            response = httpx.post(
                f"{API_URL}/evaluate",
                json=payload,
                timeout=10.0
            )

            if response.status_code == 200:

                result = response.json()

                label = result["decision_label"]
                score = result["eligibility_score"]
                confidence = result["confidence_score"]

                col1, col2, col3 = st.columns(3)

                with col1:
                    if label == "Eligible":
                        st.success(f"### {label}")
                    elif label == "Review":
                        st.warning(f"### {label}")
                    else:
                        st.error(f"### {label}")

                with col2:
                    st.metric("Eligibility Score", f"{score}/100")
                    st.progress(score / 100)

                with col3:
                    st.metric("Confidence", f"{confidence}%")
                    st.progress(confidence / 100)

                st.divider()

                st.subheader("Explanation")
                st.markdown(result["explanation_text"])

                st.divider()

                tab1, tab2, tab3 = st.tabs(
                    ["✅ Passed Rules", "❌ Failed Rules", "📊 Logic Visualization"]
                )

                with tab1:
                    for rule in result["passed_rules"]:
                        with st.expander(
                            f"{rule['name']} (+{rule['score_delta']})"
                        ):
                            st.write(f"**Reason:** {rule['reason']}")
                            st.caption(
                                f"Ref: {rule['document_reference']['doc_id']} "
                                f"p.{rule['document_reference']['page']}"
                            )

                with tab2:
                    for rule in result["failed_rules"]:
                        with st.expander(rule["name"]):
                            st.write(f"**Reason:** {rule['reason']}")
                            if rule.get("suggestion"):
                                st.info(
                                    f"💡 Suggestion: {rule['suggestion']}"
                                )
                            st.caption(
                                f"Ref: {rule['document_reference']['doc_id']} "
                                f"p.{rule['document_reference']['page']}"
                            )

                with tab3:
                    st.info("Graph visualization available if graphviz installed.")

            else:
                st.error(f"Error from API: {response.text}")

        except httpx.ConnectError:
            st.error("Could not connect to backend API. Make sure FastAPI is running.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")