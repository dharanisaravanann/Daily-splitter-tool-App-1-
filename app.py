import streamlit as st
import pandas as pd
from io import BytesIO


def split_reservations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take the original reservations df and return a daily-split df.
    This function does NOT modify the original df passed in.
    """
    # Work on a copy so df_input stays clean
    df = df.copy()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert date columns to datetime
    df["Arrival"] = pd.to_datetime(df["Arrival"], dayfirst=True, errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], dayfirst=True, errors="coerce")
    df["Booking Date"] = pd.to_datetime(df["Booking Date"], dayfirst=True, errors="coerce")

    # Create stay dates list per reservation (Arrival to day before Departure)
    df["Stay_dates"] = [
        pd.date_range(start, end - pd.Timedelta(days=1), freq="D")
        for start, end in zip(df["Arrival"], df["Departure"])
    ]

    # Explode to one row per night
    df_daily = df.explode("Stay_dates").reset_index(drop=True)

    # Turn Stay_dates into a Date column and drop the list
    df_daily["Date"] = pd.to_datetime(df_daily["Stay_dates"], errors="coerce")
    df_daily.drop(columns=["Stay_dates"], inplace=True)

    # Total nights per reservation (for revenue splitting)
    total_nights = df_daily.groupby("Reservation Number")["Date"].transform("size")

    # In the DAILY view, each row = one night
    df_daily["Nights"] = 1

    # 👉 Overwrite Base/Total Revenue with per-night values
    df_daily["Base Revenue"] = (df_daily["Base Revenue"] / total_nights).round(2)
    df_daily["Total Revenue"] = (df_daily["Total Revenue"] / total_nights).round(2)

    # Rename Channel -> Sub Channel in the daily sheet
    if "Channel" in df_daily.columns:
        df_daily = df_daily.rename(columns={"Channel": "Sub Channel"})

    # Remove Arrival and Departure from the daily split sheet
    for col in ["Arrival", "Departure"]:
        if col in df_daily.columns:
            df_daily = df_daily.drop(columns=[col])

    # Format Date and Booking Date as dd-mm-yyyy for output
    df_daily["Date"] = df_daily["Date"].dt.strftime("%d-%m-%Y")
    df_daily["Booking Date"] = df_daily["Booking Date"].dt.strftime("%d-%m-%Y")

    # Keep only the desired columns, in this exact order
    desired_cols = [
        "Reservation Number",
        "Apartment",
        "Guest Name",
        "Sub Channel",
        "Date",
        "Booking Date",
        "Nights",
        "Base Revenue",
        "Total Revenue",
    ]

    df_daily = df_daily[desired_cols]

    return df_daily


# ---------------- STREAMLIT APP ----------------

st.title("Daily Split Tool")

st.write(
    "Upload a reservations Excel file (.xlsx) and this tool will:\n"
    "- Split each booking into daily rows\n"
    "- Calculate base and total revenue per night\n"
    "- Return an Excel file with two sheets: Original Data + Reservations Daily Split."
)

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read original input
        df_input = pd.read_excel(uploaded_file)

        st.subheader("Preview of uploaded data")
        st.dataframe(df_input.head())

        # Build daily split
        df_output = split_reservations(df_input)

        st.subheader("Preview of daily split (first 20 rows)")
        st.dataframe(df_output.head(20))

        # ----- Build Excel with TWO SHEETS in memory -----
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # ORIGINAL DATA SHEET (clean dates, no Stay_dates)
            df_original = df_input.copy()
            df_original.columns = df_original.columns.str.strip()

            # Format dates as dd-mm-yyyy (remove time)
            for col in ["Arrival", "Departure", "Booking Date"]:
                df_original[col] = pd.to_datetime(
                    df_original[col], dayfirst=True, errors="coerce"
                ).dt.strftime("%d-%m-%Y")

            # Ensure no Stay_dates column in the original sheet
            if "Stay_dates" in df_original.columns:
                df_original = df_original.drop(columns=["Stay_dates"])

            df_original.to_excel(writer, sheet_name="Original Data", index=False)

            # DAILY SPLIT SHEET
            df_output.to_excel(writer, sheet_name="Reservations Daily Split", index=False)

        buffer.seek(0)

        st.download_button(
            label="📥 Download Excel (Original + Daily Split)",
            data=buffer,
            file_name="reservations_with_daily_split.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        st.error(f"Something went wrong: {e}")

else:
    st.info("Please upload an Excel file to begin.")

