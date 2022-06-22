import pandas as pd
from datetime import date
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import matplotlib


def get_amortization_table(interest_rate, years, payments_year, principal, addl_principal=0, start_date=date.today()):
    """ Calculate the amortization schedule given the loan details

     Args:
        interest_rate: The annual interest rate for this loan
        years: Number of years for the loan
        payments_year: Number of payments in a year
        principal: Amount borrowed
        addl_principal (optional): Additional payments to be made each period. Assume 0 if nothing provided.
                                   must be a value less then 0, the function will convert a positive value to
                                   negative
        start_date (optional): Start date. Will start on first of next month if none provided

    Returns:
        schedule: Amortization schedule as a pandas dataframe
        summary: Pandas dataframe that summarizes the payoff information
    """
    # Ensure the additional payments are negative
    if addl_principal > 0:
        addl_principal = -addl_principal

    # Create an index of the payment dates
    rng = pd.date_range(start_date, periods=years * payments_year, freq='MS')
    rng.name = "Payment_Date"

    # Build up the Amortization schedule as a DataFrame
    df = pd.DataFrame(index=rng, columns=['Payment', 'Principal', 'Interest',
                                          'Addl_Principal', 'Curr_Balance'], dtype='float')

    # Add index by period (start at 1 not 0)
    df.reset_index(inplace=True)
    df.index += 1
    df.index.name = "Period"

    # Calculate the payment, principal and interests amounts using built in Numpy functions
    per_payment = npf.pmt(interest_rate / payments_year, years * payments_year, principal)
    df["Payment"] = per_payment
    df["Principal"] = npf.ppmt(interest_rate / payments_year, df.index, years * payments_year, principal)
    df["Interest"] = npf.ipmt(interest_rate / payments_year, df.index, years * payments_year, principal)

    # Round the values
    df = df.round(2)

    # Add in the additional principal payments
    df["Addl_Principal"] = addl_principal

    # Store the Cumulative Principal Payments and ensure it never gets larger than the original principal
    df["Cumulative_Principal"] = (df["Principal"] + df["Addl_Principal"]).cumsum()
    df["Cumulative_Principal"] = df["Cumulative_Principal"].clip(lower=-principal)

    # Calculate the current balance for each period
    df["Curr_Balance"] = principal + df["Cumulative_Principal"]

    # Determine the last payment date
    try:
        last_payment = df.query("Curr_Balance <= 0")["Curr_Balance"].idxmax(axis=1, skipna=True)
    except ValueError:
        last_payment = df.last_valid_index()

    last_payment_date = "{:%m-%d-%Y}".format(df.loc[last_payment, "Payment_Date"])

    # Truncate the data frame if we have additional principal payments:
    if addl_principal != 0:
        # Remove the extra payment periods
        df = df.loc[0:last_payment].copy()

        # Calculate the principal for the last row
        df.loc[last_payment, "Principal"] = -(df.loc[last_payment - 1, "Curr_Balance"])

        # Calculate the total payment for the last row
        df.loc[last_payment, "Payment"] = df.loc[last_payment, ["Principal", "Interest"]].sum()

        # Zero out the additional principal
        df.loc[last_payment, "Addl_Principal"] = 0

    # Get the payment info into a DataFrame in column order
    payment_info = (df[["Payment", "Principal", "Addl_Principal", "Interest"]]
                    .sum().to_frame().T)

    # Format the Date DataFrame
    payment_details = pd.DataFrame.from_dict(dict([('payoff_date', [last_payment_date]),
                                                   ('Interest Rate', [interest_rate]),
                                                   ('Number of years', [years])
                                                   ]))
    # Add a column showing how much we pay each period.
    # Combine addl principal with principal for total payment
    payment_details["Period_Payment"] = round(per_payment, 2) + addl_principal

    payment_summary = pd.concat([payment_details, payment_info], axis=1)
    return df, payment_summary


def get_annual_payment_df(schedule):
    annual_schedule = schedule.set_index('Payment_Date').resample("A")["Interest", "Principal"].sum().abs().reset_index()
    annual_schedule["Year"] = annual_schedule["Payment_Date"].dt.year
    # print(annual_schedule.head())

    return annual_schedule


def get_annual_net_interest_df(schedule):
    annual_net_interest_schedule = schedule.set_index('Payment_Date').resample("A")["Interest"].sum().abs().reset_index()
    annual_net_interest_schedule["Year"] = annual_net_interest_schedule["Payment_Date"].dt.year
    annual_net_interest_schedule["Purpose"] = "Test"
    # print(annual_net_interest_schedule.head())

    return annual_net_interest_schedule


def get_net_interest_income_df(df):
    df_loan_2 = df.copy()
    net_interest_income_df = pd.DataFrame(columns=["Payment_Date", "Interest", "Year", "Purpose", "Loan ID"])
    for row in df_loan_2.itertuples(index=True, name='Pandas'):
        net_interest_rate = row.interest_rate - (row.ten_yr_treasury_index_date_funded / 100)
        schedule_df, stats = get_amortization_table(net_interest_rate, row.duration_years, 12,
                                                            row.funded_amount, addl_principal=0,
                                                            start_date=row.funded_date)
        annual_net_interest_income_schedule_df = get_annual_net_interest_df(schedule_df)
        annual_net_interest_income_schedule_df['Purpose'] = row.purpose
        annual_net_interest_income_schedule_df['Loan ID'] = row.loan_id
        net_interest_income_df = pd.concat([net_interest_income_df, annual_net_interest_income_schedule_df])
    net_interest_income_df.to_csv('data/net_interest_income.csv', index=False)


if __name__ == "__main__":
    schedule1, stats1 = get_amortization_table(0.05, 30, 12, 100000, addl_principal=0)
    get_annual_net_interest_df(schedule1)
    # print(schedule1.head())
    # print(schedule1.tail())
    # print(stats1)




