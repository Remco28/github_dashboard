Title: Fix Achievements card spacing (collapse unused grid space)

Context
- The Achievements section renders badge cards. A recent visual bug was fixed, but spacing remains off when there are few badges (e.g., one card leaves a wide, awkward empty area to the right, as shown in the screenshot).
- Current implementation in `ui/gamification.py` uses `st.columns(...)` with inline styles. We also ship CSS for `.gd-badges`/`.gd-badge`, but that class-based grid isn’t used.

Problem
- `st.columns(...)` doesn’t pack items tightly or control horizontal whitespace well. With one or two badges, the layout looks sparse and misaligned.
- Earlier class-based grid CSS used `auto-fill`, which keeps empty tracks and visually looks like “extra columns” of space.

Goal
- Make the Achievements layout compact and consistent for 1–N badges by collapsing unused grid tracks and packing items left with a predictable, small gap.

Scope of change
- Files: `ui/gamification.py`
- Update both the CSS rules injected by `ensure_badge_styles()` and the rendering in `render_badges(...)`.

Required changes
1) Update CSS grid to collapse unused space and use fixed-width tracks
   - In `ensure_badge_styles()` replace the `.gd-badges` rule with:
     - `grid-template-columns: repeat(auto-fit, minmax(140px, 140px));`
     - `gap: 12px;`
     - `margin: 8px 0;`
     - `justify-content: start;`  (packs items to the left without huge trailing space)
   - Keep `.gd-badge` square, centered content. Remove inline duplication—prefer the class.

   Pseudocode patch:
   ```python
   # in ensure_badge_styles()
   .gd-badges {
       display: grid;
       grid-template-columns: repeat(auto-fit, minmax(140px, 140px));
       gap: 12px;
       margin: 8px 0;
       justify-content: start;
   }
   .gd-badge {
       display: flex;
       flex-direction: column;
       align-items: center;
       justify-content: center;
       padding: 10px 12px;
       border: 1px solid rgba(0,0,0,0.08);
       border-radius: 10px;
       background: linear-gradient(180deg, #fff, #fafafa);
       box-shadow: 0 1px 2px rgba(0,0,0,0.04);
       aspect-ratio: 1; /* square cards */
       width: 140px;    /* matches track width */
   }
   .gd-badge-emoji { font-size: 28px; line-height: 1; margin-bottom: 6px; }
   .gd-badge-label { font-weight: 600; text-align: center; font-size: 13px; }
   ```

2) Render badges using the grid container instead of `st.columns`
   - Replace the per-column rendering with a single HTML block that emits:
     ```html
     <div class="gd-badges">
       <div class="gd-badge">
         <div class="gd-badge-emoji">{badge.emoji}</div>
         <div class="gd-badge-label">{badge.label}</div>
       </div>
       ...
     </div>
     ```
   - Keep `help=badge.description` by attaching it to the surrounding `st.markdown` call or by omitting `help` (Streamlit does not attach tooltip to inner HTML nodes). If a tooltip is desired, render each badge as its own `st.markdown(..., help=...)` inside the grid string (acceptable since badges are few) or drop the help to keep markup simple.

   Pseudocode patch:
   ```python
   def render_badges(badges: List[Badge]) -> None:
       if not badges:
           st.info("🏆 Complete coding activities to earn badges!")
           return
       ensure_badge_styles()
       items = "\n".join(
           f"<div class='gd-badge'><div class='gd-badge-emoji'>{b.emoji}</div><div class='gd-badge-label'>{b.label}</div></div>"
           for b in badges
       )
       st.markdown(f"<div class='gd-badges'>{items}</div>", unsafe_allow_html=True)
   ```

Why this works
- `auto-fit` collapses unused tracks; with one badge, there are no empty “phantom columns”, so you don’t see a wide, awkward gap to the right.
- Fixed 140px tracks keep cards at a consistent, compact size; they wrap naturally as the viewport shrinks.
- Using a single grid container removes the extra horizontal gutters from `st.columns(...)` and avoids per-column vertical misalignment.

Acceptance criteria
- With 1 badge: the card sits left-aligned under the header with normal page margins and no exaggerated empty space.
- With 2–8 badges: cards flow in rows with a uniform 12px gap; wrapping is clean.
- No visible raw HTML appears on the page; the style injection remains silent.

Out of scope
- Changing badge content or award logic.
- Adding hover tooltips to the inner HTML elements beyond Streamlit’s `help` limitations.

Notes for Dev
- Remove the now-redundant inline styles inside `render_badges` once the class-based grid is used.
- If you prefer slightly larger cards, bump 140px to 160px in both the `minmax(...)` and `.gd-badge { width: ... }` to keep them square.

After implementation
- Manually verify Achievements with 0, 1, 3, and 7 badges.
- Confirm that other sections’ spacing (headers, nudges) are unaffected.

