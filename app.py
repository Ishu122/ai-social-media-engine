import streamlit as st
import anthropic
import json
import csv
import io

st.set_page_config(
    page_title="AI Social Media Engine",
    page_icon="✨",
    layout="centered"
)

st.markdown("""
<style>
    .block-container { max-width: 780px; padding-top: 2rem; }
    .viral-label { font-size: 13px; color: #666; margin-bottom: 4px; }
    .chip { display: inline-block; background: #f0f0f0; border-radius: 20px; padding: 3px 10px; font-size: 12px; margin: 2px; color: #444; }
    .section-header { font-size: 15px; font-weight: 600; margin-bottom: 0.5rem; }
    .tip-item { font-size: 14px; color: #555; margin-bottom: 6px; }
    div[data-testid="stTabs"] button { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## ✨ AI Social Media Engine v2")
st.markdown("Content → posts, viral score, image prompts & schedule — all in one click.")
st.divider()

with st.form("main_form"):
    content = st.text_area(
        "Your content",
        placeholder="Paste a blog post, topic, idea, or anything you want to repurpose...",
        height=140,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        tone = st.selectbox("Tone", ["Casual", "Professional", "Bold & punchy", "Storytelling"])
    with col2:
        audience = st.selectbox("Audience", ["Founders & marketers", "Developers", "General public", "B2B decision makers"])
    with col3:
        platform = st.selectbox("Platforms", ["All platforms", "LinkedIn only", "Twitter/X only", "Instagram only", "Newsletter only"])

    api_key = st.text_input("Anthropic API key", type="password", help="Get yours at console.anthropic.com")
    submitted = st.form_submit_button("✨ Generate posts", use_container_width=True, type="primary")

if submitted:
    if not content.strip():
        st.warning("Please enter some content first.")
        st.stop()
    if not api_key.strip():
        st.warning("Please enter your Anthropic API key.")
        st.stop()

    platform_map = {
        "All platforms": "all platforms: LinkedIn, Twitter/X, Instagram, Newsletter",
        "LinkedIn only": "LinkedIn only",
        "Twitter/X only": "Twitter/X only",
        "Instagram only": "Instagram only",
        "Newsletter only": "Newsletter only"
    }

    prompt = f"""You are an expert social media strategist. Given this content, generate everything needed for a full content campaign.

Content: {content}
Tone: {tone}
Target audience: {audience}
Platforms requested: {platform_map[platform]}

Respond ONLY with a valid JSON object, no markdown, no backticks, no preamble:
{{
  "linkedin": "LinkedIn post (200-250 words, hook first line, short paragraphs, end with a question)",
  "twitter": "Tweet 1/5: bold claim\\n\\nTweet 2/5: expand the idea\\n\\nTweet 3/5: practical example\\n\\nTweet 4/5: actionable tip\\n\\nTweet 5/5: CTA + link placeholder",
  "instagram": "Instagram caption with storytelling angle, 100-130 words, then line break, then 5 hashtags",
  "newsletter": "Subject: [catchy subject line]\\n\\n[150-180 word newsletter snippet with clear value and CTA]",
  "viral_scores": {{ "linkedin": 78, "twitter": 65, "instagram": 82, "newsletter": 55 }},
  "improvement_tips": ["tip 1", "tip 2", "tip 3"],
  "best_times": ["LinkedIn: Tue-Thu 8-10am", "Twitter: Mon-Fri 12-1pm", "Instagram: Wed-Fri 6-8pm", "Newsletter: Tuesday 7am"],
  "image_prompts": {{
    "linkedin": "image prompt for linkedin here --v 6",
    "twitter": "image prompt for twitter here --v 6",
    "instagram": "image prompt for instagram here --v 6"
  }},
  "schedule": [
    {{ "day": "Monday", "time": "9:00 AM", "platform": "LinkedIn", "note": "reason" }},
    {{ "day": "Tuesday", "time": "12:00 PM", "platform": "Twitter/X", "note": "reason" }},
    {{ "day": "Wednesday", "time": "7:00 AM", "platform": "Newsletter", "note": "reason" }},
    {{ "day": "Friday", "time": "6:00 PM", "platform": "Instagram", "note": "reason" }}
  ]
}}"""

    with st.spinner("Generating your full content campaign..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)

        except json.JSONDecodeError:
            st.error("Couldn't parse AI response. Please try again.")
            st.stop()
        except anthropic.AuthenticationError:
            st.error("Invalid API key. Check and try again.")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.stop()

    st.divider()
    st.markdown("### Your content campaign is ready")

    platform_keys = {
        "All platforms": ["linkedin", "twitter", "instagram", "newsletter"],
        "LinkedIn only": ["linkedin"],
        "Twitter/X only": ["twitter"],
        "Instagram only": ["instagram"],
        "Newsletter only": ["newsletter"]
    }
    show = platform_keys[platform]

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Posts", "🔥 Viral score", "🎨 Image prompts", "📅 Schedule"])

    with tab1:
        icons = {"linkedin": "💼", "twitter": "🐦", "instagram": "📸", "newsletter": "📧"}
        labels = {"linkedin": "LinkedIn", "twitter": "Twitter / X thread", "instagram": "Instagram caption", "newsletter": "Newsletter snippet"}
        for p in show:
            if result.get(p):
                st.markdown(f"**{icons[p]} {labels[p]}**")
                st.text_area(label=labels[p], value=result[p], height=200, label_visibility="collapsed", key=f"post_{p}")

    with tab2:
        scores = result.get("viral_scores", {})
        st.markdown("**Predicted viral potential**")
        for p in ["linkedin", "twitter", "instagram", "newsletter"]:
            score = int(scores.get(p, 0))
            color = "normal" if score >= 75 else "off" if score >= 50 else "inverse"
            st.markdown(f"<p class='viral-label'>{p.capitalize()} — {score}/100</p>", unsafe_allow_html=True)
            st.progress(score / 100)

        st.markdown("**Improvement tips**")
        for tip in result.get("improvement_tips", []):
            st.markdown(f"<p class='tip-item'>• {tip}</p>", unsafe_allow_html=True)

        st.markdown("**Best posting times**")
        times_html = " ".join([f"<span class='chip'>{t}</span>" for t in result.get("best_times", [])])
        st.markdown(times_html, unsafe_allow_html=True)

    with tab3:
        prompts = result.get("image_prompts", {})
        img_icons = {"linkedin": "💼", "twitter": "🐦", "instagram": "📸"}
        for p in ["linkedin", "twitter", "instagram"]:
            if prompts.get(p):
                st.markdown(f"**{img_icons[p]} {p.capitalize()} image prompt**")
                st.text_area(
                    label=p,
                    value=prompts[p],
                    height=100,
                    label_visibility="collapsed",
                    key=f"img_{p}",
                    help="Paste this into Midjourney, DALL-E, or Ideogram"
                )

    with tab4:
        schedule = result.get("schedule", [])
        if schedule:
            st.markdown("**Recommended posting schedule**")
            for item in schedule:
                col_a, col_b, col_c, col_d = st.columns([1.2, 1, 1.2, 3])
                col_a.markdown(f"**{item.get('day','')}**")
                col_b.markdown(item.get('time',''))
                col_c.markdown(f"`{item.get('platform','')}`")
                col_d.markdown(f"<span style='color:#666; font-size:13px;'>{item.get('note','')}</span>", unsafe_allow_html=True)

            st.divider()
            csv_buf = io.StringIO()
            writer = csv.DictWriter(csv_buf, fieldnames=["day","time","platform","note"])
            writer.writeheader()
            writer.writerows(schedule)
            st.download_button(
                label="⬇️ Download schedule as CSV",
                data=csv_buf.getvalue(),
                file_name="posting_schedule.csv",
                mime="text/csv"
            )

st.divider()
st.markdown("<p style='text-align:center; color: #aaa; font-size: 12px;'>Built with Claude API · github.com/Ishu122</p>", unsafe_allow_html=True)
