# 🎀 Kawaii Pink Scientific Calculator

A baby-pink and hot-pink scientific calculator built with Streamlit.

## Run it

**Windows:** double-click `run.bat`
**Mac/Linux:** `bash run.sh`
**Manually:**

```
pip install -r requirements.txt
streamlit run app.py
```

## Keyboard (just type!)

The display is a real text box, so type expressions the natural way:

`sin(30)+2^3`, `sqrt(16)`, `5!`, `pi*2`, `nCr(5,2)`, `log(1000)`, `2e3`

| Key | Action |
|---|---|
| `Enter` or `=` | calculate |
| `Esc` | clear |
| `Backspace` | delete (removes whole `sin(` etc.) |
| `↑` / `↓` | recall previous calculations |
| `* / -` | shown as `× ÷ −` |
| operator right after a result | continues from `Ans` |

Typing works even if you have not clicked the calculator.
Unclosed brackets are closed automatically.

## Functions

sin cos tan, sin⁻¹ cos⁻¹ tan⁻¹, sinh cosh tanh, ln, log, log₂, 10ˣ, eˣ, √, ∛, ʸ√x,
x², x³, xʸ, n!, 1/x, |x|, nCr, nPr, mod, %, π, e, Rand, Ans, EXP,
DEG/RAD switch, memory (MC MR M+ M−) and a history that is remembered between visits.
There is also a tiny bubble-pop sound toggle (🔔).

## Your own background picture

Drop an image called `background.jpg` (or png / webp) into `assets/background/`,
or upload one in the sidebar while the app runs. Use an image you have rights to.
Without one, you get the pink polka-dot background with the bubble mascot.

## Files

```
app.py                  the app
assets/icons/           bubble, heart, star, sparkle and bow icons (SVG)
assets/mascot_bunny.svg original mascot
assets/background/      put your background image here
.streamlit/config.toml  pink theme
```
