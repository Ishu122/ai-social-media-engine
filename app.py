import streamlit as st
import anthropic
import json

st.set_page_config(
    page_title="AI Social Media Engine",
    page_icon="✨",
    layout="centered"
)

st.markdown("""
<style>
    .main { max-width: 750px; margin: 0 auto; }
    .output-box {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        font-size: 14px;
        line-height: 1.7;
        white-space: pre-wrap;
        margin-bottom: 1rem;
    }
    .platform-label {
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 6px;
    }
    .badge {
        background: #d4edda;
        color: #155724;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("## ✨ AI Social Media Engine")
st.markdown("Paste any content → get posts for every platform instantly.")
st.markdown("---")

content = st.text_area(
    "Your content",
    placeholder="e.g. I built an AI tool that generates social media posts from a single idea. It saves me 3 hours a week...",
    height=150,
    help="Paste a topic, blog post, idea, or anything you want to repurpose."
)

col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Tone", ["Casual", "Professional", "Bold & punchy", "Storytelling"])
with col2:
    platform = st.selectbox("Platforms", ["All platforms", "LinkedIn only", "Twitter/X only", "Instagram only", "Newsletter only"])

api_key = st.text_input("Anthropic API Key", type="password", help="Get yours at console.anthropic.com")

generate = st.button("Generate posts ✨", use_container_width=True, type="primary")

if generate:
    if not content.strip():
        st.warning("Please enter some content first.")
    elif not api_key.strip():
        st.warning("Please enter your Anthropic API key.")
    else:
        platform_map = {
            "All platforms": "LinkedIn, Twitter/X thread, Instagram caption, Newsletter snippet",
            "LinkedIn only": "LinkedIn post only",
            "Twitter/X only": "Twitter/X thread only",
            "Instagram only": "Instagram caption only",
            "Newsletter only": "Newsletter snippet only"
        }

        prompt = f"""You are a social media content expert. Based on the content below, generate posts for: {platform_map[platform]}.

Tone: {tone}

Content:
{content}

Respond ONLY with a valid JSON object, no markdown, no backticks, no explanation. Format:
{{
  "linkedin": "full linkedin post (200-300 words, hook opening, short paragraphs, end with question)",
  "twitter": "Tweet 1/5: bold claim\\n\\nTweet 2/5: insight\\n\\nTweet 3/5: example\\n\\nTweet 4/5: tip\\n\\nTweet 5/5: CTA",
  "instagram": "storytelling caption (100-150 words) + 5 relevant hashtags",
  "newsletter": "newsletter snippet (150-200 words) with subject line suggestion at top"
}}

If a platform was not requested, return an empty string for that key."""

        with st.spinner("Generating your posts..."):
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

                st.markdown("---")
                st.markdown("### Your posts are ready!")

                platforms_to_show = {
                    "All platforms": ["linkedin", "twitter", "instagram", "newsletter"],
                    "LinkedIn only": ["linkedin"],
                    "Twitter/X only": ["twitter"],
                    "Instagram only": ["instagram"],
                    "Newsletter only": ["newsletter"]
                }

                icons = {
                    "linkedin": "💼 LinkedIn",
                    "twitter": "🐦 Twitter / X Thread",
                    "instagram": "📸 Instagram Caption",
                    "newsletter": "📧 Newsletter Snippet"
                }

                for p in platforms_to_show[platform]:
                    if result.get(p):
                        st.markdown(f"**{icons[p]}**")
                        st.text_area(
                            label=icons[p],
                            value=result[p],
                            height=200,
                            label_visibility="collapsed",
                            key=f"output_{p}"
                        )

            except json.JSONDecodeError:
                st.error("Couldn't parse the response. Please try again.")
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align:center; color: gray; font-size: 12px;'>Built with Claude API · github.com/Ishu122</p>", unsafe_allow_html=True)
