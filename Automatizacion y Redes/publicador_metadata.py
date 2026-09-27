"""
Continuum Lab - Metadata & Algorithmic Hashtags Publisher Engine
Generates optimized titles, descriptions, and tag payloads tailored for YouTube Shorts, Instagram Reels & TikTok.
"""
import json
import os

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "hashtags_master.json")

def load_catalog():
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def generate_social_payload(video_id, title_concept, topic="fourier_series"):
    catalog = load_catalog()
    
    if topic == "fourier_series":
        yt_title = "Drawing ANY Shape with Rotating Circles | Fourier Series Epicycles #Shorts"
        yt_description = (
            "Can rotating circles draw ANY geometric shape? 📐✨\n\n"
            "Every continuous periodic 2D contour can be decomposed into an infinite sum of rotating complex vectors (epicycles). "
            "As harmonic order N increases, the superposition converges onto the target contour via discrete Fourier transform coefficients:\n\n"
            "f(t) = a₀ + Σ [ aₙ cos(nωt) + bₙ sin(nωt) ]\n\n"
            "Which geometric curve or polygon should we reconstruct next?\n\n"
            "🔬 Mathematical Modeling: Continuum Lab\n"
            "⚙️ Framework: Python / Manim Community (60 FPS)\n"
            "📐 Topic: Geometric Fourier Series & Harmonic Analysis\n\n"
            "---\n"
            "#shorts #fourier #fourierseries #math #mathematics #mathart #satisfying #calculus #geometry #3blue1brown #physics #engineering #continuumlab"
        )
        yt_tags = [
            "ContinuumLab", "FourierSeries", "Epicycles", "MathArt", "Manim", 
            "3Blue1BrownStyle", "ComputationalPhysics", "Mathematics", "SatisfyingMath", 
            "Geometry", "HarmonicAnalysis", "PythonManim", "STEM", "Calculus"
        ]
        
        ig_caption = (
            "Can rotating circles draw ANY shape? 📐✨\n\n"
            "Every periodic geometric contour can be decomposed into an infinite sum of rotating phasors (epicycles). "
            "By computing the Fourier series coefficients, complex trajectories emerge purely from circular motion:\n\n"
            "f(t) = a₀ + Σ [ aₙ cos(nωt) + bₙ sin(nωt) ]\n\n"
            "Notice how higher harmonics capture sharp corners (Gibbs phenomenon).\n\n"
            "Which shape should we synthesize next?\n\n"
            "🔬 Continuum Lab (@continuumlab_)\n"
            "⚙️ Engine: Python / Manim Community 60 FPS\n\n"
            "#fourierseries #math #physics #mathematics #mathart #satisfying #stem #engineering #geometry #calculus #3blue1brown #python #simulation #generativeart #continuumlab"
        )
        
        tt_caption = (
            "Can rotating circles draw ANY shape? 📐✨ Fourier Epicycles in computational geometry. What shape next? "
            "#math #physics #engineering #satisfying #fourier #stem #learnontiktok #scitok #continuumlab"
        )
        
    else:
        # Default / Fluid mechanics
        yt_title = f"{title_concept} | Continuum Lab #Shorts"
        yt_description = (
            f"{title_concept} computed via high-order physical simulation.\n\n"
            f"🔬 Physical Modeling: Continuum Lab\n"
            f"⚙️ Framework: Navier-Stokes / Lattice Boltzmann / Manim 60 FPS\n\n"
            f"---\n"
            f"#shorts #physics #fluiddynamics #manim #engineering #simulation #science #stem #math"
        )
        yt_tags = catalog.get("youtube_shorts", {}).get("tags", [])
        ig_caption = f"{title_concept}\n\nSimulation by Continuum Lab (@continuumlab_).\n\n#physics #fluiddynamics #simulation #engineering #continuumlab"
        tt_caption = f"{title_concept} 🌊🔬 #physics #fluiddynamics #engineering #simulation #continuumlab"

    return {
        "video_id": video_id,
        "youtube": {
            "title": yt_title,
            "description": yt_description,
            "tags": yt_tags,
            "category_id": "28", # Science & Technology
            "privacy_status": "public"
        },
        "instagram": {
            "caption": ig_caption
        },
        "tiktok": {
            "caption": tt_caption,
            "sound_recommendations": "Cyberpunk / Synthwave ambient / Phonk instrumental / Lo-fi precision"
        }
    }

if __name__ == "__main__":
    example = generate_social_payload(video_id="01", title_concept="Geometric Fourier Series", topic="fourier_series")
    print(json.dumps(example, indent=2, ensure_ascii=False))
