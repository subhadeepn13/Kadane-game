import random
import streamlit as st

# ----------------------------
# Helpers
# ----------------------------

def generate_array(n: int = 9, low: int = -9, high: int = 9):
    """Generate a random array with no zeros (so every tile changes coins)."""
    nums = []
    while len(nums) < n:
        x = random.randint(low, high)
        if x != 0:
            nums.append(x)
    return nums


def kadane(nums):
    """Return (best_sum, best_start_idx, best_end_idx)."""
    best_sum = nums[0]
    current_sum = nums[0]
    best_start = best_end = 0
    current_start = 0

    for i in range(1, len(nums)):
        # Decide: start fresh here OR continue
        if nums[i] > current_sum + nums[i]:
            current_sum = nums[i]
            current_start = i
        else:
            current_sum += nums[i]

        # Update best if needed
        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = i

    return best_sum, best_start, best_end


def render_array(nums, current_range=None, best_range=None):
    """
    Show the numbers as colored boxes.
    current_range: (start, end) of walking slice
    best_range: (start, end) of best slice so far
    """
    cols = st.columns(len(nums))
    for i, (col, val) in enumerate(zip(cols, nums)):
        in_current = current_range is not None and current_range[0] <= i <= current_range[1]
        in_best = best_range is not None and best_range[0] <= i <= best_range[1]

        # Simple color rules
        if in_current and in_best:
            bg = "#e9d5ff"  # both
        elif in_best:
            bg = "#bbf7d0"  # best slice
        elif in_current:
            bg = "#bfdbfe"  # walking slice
        else:
            bg = "#f1f5f9"  # normal

        col.markdown(
            f"""
            <div style="
                text-align:center;
                padding:8px;
                border-radius:10px;
                background:{bg};
                border:1px solid #cbd5e1;
                ">
                <div style="font-size:11px; color:#64748b;">idx {i}</div>
                <div style="font-size:22px; font-weight:600;">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def reset_kadane_state():
    """Initialize step-by-step Kadane state in session_state."""
    nums = st.session_state.nums
    st.session_state.kadane_idx = 0
    st.session_state.current_sum = nums[0]
    st.session_state.best_sum = nums[0]
    st.session_state.current_start = 0
    st.session_state.best_start = 0
    st.session_state.best_end = 0
    st.session_state.last_step_info = (
        f"We start at index 0 with number {nums[0]}. "
        f"Current sum = {nums[0]}, best sum so far = {nums[0]}."
    )


def reset_game():
    """Create new numbers and reset Kadane walk."""
    st.session_state.nums = generate_array()
    reset_kadane_state()


def advance_kadane_step():
    """Move one step in Kadane's algorithm (for step-by-step mode)."""
    nums = st.session_state.nums
    idx = st.session_state.kadane_idx

    # Already at the end
    if idx >= len(nums) - 1:
        st.session_state.last_step_info = (
            f"We are done walking! The best sum is {st.session_state.best_sum}, "
            f"from indexes {st.session_state.best_start} to {st.session_state.best_end}."
        )
        return

    i = idx + 1
    curr_sum = st.session_state.current_sum
    best_sum = st.session_state.best_sum
    curr_start = st.session_state.current_start
    best_start = st.session_state.best_start
    best_end = st.session_state.best_end

    # Two choices: start fresh or continue the old path
    option_continue = curr_sum + nums[i]
    option_new = nums[i]

    if option_new > option_continue:
        new_curr_sum = option_new
        new_curr_start = i
        choice_text = (
            f"It's better to START FRESH at index {i} (number {nums[i]}), "
            f"instead of keeping the old total."
        )
    else:
        new_curr_sum = option_continue
        new_curr_start = curr_start
        choice_text = (
            f"We KEEP WALKING and add number {nums[i]} to our current path."
        )

    # Check if this becomes the new best sum
    improved = False
    if new_curr_sum > best_sum:
        new_best_sum = new_curr_sum
        new_best_start = new_curr_start
        new_best_end = i
        improved = True
    else:
        new_best_sum = best_sum
        new_best_start = best_start
        new_best_end = best_end

    # Save back to session_state
    st.session_state.kadane_idx = i
    st.session_state.current_sum = new_curr_sum
    st.session_state.current_start = new_curr_start
    st.session_state.best_sum = new_best_sum
    st.session_state.best_start = new_best_start
    st.session_state.best_end = new_best_end

    extra = ""
    if improved:
        extra = f" 🎉 Now this is the BEST sum so far: {new_best_sum}."

    st.session_state.last_step_info = (
        f"Looking at index {i}, number {nums[i]}. {choice_text} "
        f"Current path sum = {new_curr_sum}. Best sum so far = {new_best_sum}.{extra}"
    )


# ----------------------------
# UI Sections
# ----------------------------

def play_game():
    st.subheader("🎯 Game: Find the Best Coin Path")

    st.write(
        "Think of each number as a tile on the ground. "
        "Positive = you **gain** coins, negative = you **lose** coins.\n\n"
        "Pick one continuous stretch of tiles so your total coins is as big as possible."
    )

    nums = st.session_state.nums
    render_array(nums)

    st.write("👣 Choose where your path starts and ends (indexes are 0-based).")

    start_idx, end_idx = st.slider(
        "Pick your path (start and end index)",
        min_value=0,
        max_value=len(nums) - 1,
        value=(0, len(nums) - 1),
    )

    if start_idx > end_idx:
        st.warning("Start index must be ≤ end index.")
        return

    user_slice = nums[start_idx : end_idx + 1]
    user_sum = sum(user_slice)

    st.write(f"Your chosen numbers: `{user_slice}`")
    st.write(f"Your total coins from this path: **{user_sum}**")

    if st.button("✅ Check my answer"):
        best_sum, best_start, best_end = kadane(nums)
        best_slice = nums[best_start : best_end + 1]

        st.write("---")
        if user_sum == best_sum and start_idx == best_start and end_idx == best_end:
            st.success(
                f"Perfect! 🎉 You picked the best path: {best_slice} "
                f"with total coins **{best_sum}**."
            )
        elif user_sum == best_sum:
            st.info(
                f"Nice! Your path has the best total **{user_sum}**. "
                f"One best path is {best_slice} (indexes {best_start}–{best_end})."
            )
        else:
            st.error(
                f"Not quite. Your path gives **{user_sum}** coins, "
                f"but the best path gives **{best_sum}** coins from {best_slice} "
                f"(indexes {best_start}–{best_end})."
            )
        st.caption(
            "Hint: If a number makes your total go too low, it might be better to "
            "start a new path after it."
        )


def kadane_walk_ui():
    st.subheader("🧠 Learn: Step-by-Step Walk (Kadane)")

    nums = st.session_state.nums

    if "current_sum" not in st.session_state:
        reset_kadane_state()

    current_range = (st.session_state.current_start, st.session_state.kadane_idx)
    best_range = (st.session_state.best_start, st.session_state.best_end)

    st.write("Boxes in **blue** = your current walking path.")
    st.write("Boxes in **green** = best path found so far.")
    st.write("Boxes in **purple** = both current and best (same path).")

    render_array(nums, current_range=current_range, best_range=best_range)

    st.write(f"📍 Current index: **{st.session_state.kadane_idx}**")
    st.write(f"👣 Current path sum: **{st.session_state.current_sum}**")
    st.write(f"🏆 Best sum so far: **{st.session_state.best_sum}**")

    st.info(st.session_state.last_step_info)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Next step"):
            advance_kadane_step()
    with col2:
        if st.button("🔁 Reset walk"):
            reset_kadane_state()


def about_section():
    st.subheader("ℹ️ What is this game teaching?")

    st.markdown(
        """
- You are learning the **Maximum Subarray Problem**:
  - Find a continuous slice of numbers with the **largest total**.
- The game shows how computers solve it quickly using something called **Kadane’s Algorithm**:
  - Walk through the numbers from left to right.
  - At each step, decide:
    - “Should I **continue** my current path?”
    - Or “Should I **start fresh** from this number?”
- This is a tiny example of **dynamic programming**:
  - You use what you already know (previous best sums) to make the next decision smarter.
        """
    )
    st.caption("You’re basically doing DP without scary math words 😄")


# ----------------------------
# Main App
# ----------------------------

def main():
    st.set_page_config(page_title="Maximum Subarray Game", page_icon="🎮", layout="wide")

    st.title("🎮 Maximum Subarray Game – Coin Path")

    # Initialize numbers once
    if "nums" not in st.session_state:
        reset_game()

    st.sidebar.header("Controls")
    st.sidebar.button("🎲 New numbers", on_click=reset_game)
    st.sidebar.write("Click this to get a fresh set of tiles.")

    tab1, tab2, tab3 = st.tabs(["🎯 Play Game", "🧠 Learn Kadane", "ℹ️ About"])

    with tab1:
        play_game()
    with tab2:
        kadane_walk_ui()
    with tab3:
        about_section()


if __name__ == "__main__":
    main()
