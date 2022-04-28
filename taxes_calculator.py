"""Calculate taxes and the final revenue"""


MININUM_WAGE = 1212.00
IRRF_TABLE = [
    {"start": 0,       "end": 1903.98, "tax": 0, "deduct": 0},
    {"start": 1903.98, "end": 2826.65, "tax": 0.075, "deduct": 142.8},
    {"start": 2826.66, "end": 3751.05, "tax": 0.15, "deduct": 354.8},
    {"start": 3751.06, "end": 4664.68, "tax": 0.225, "deduct": 636.13},
    {"start": 4664.69, "end": float("inf"), "tax": 0.275, "deduct": 869.36}
]
INSS_TABLE = [
    {"start": 0,       "end": 1100.00, "tax": 0.075},
    {"start": 1100.01, "end": 2203.48, "tax": 0.09},
    {"start": 2203.49, "end": 3305.22, "tax": 0.12},
    {"start": 3305.23, "end": 6433.57, "tax": 0.14}
]
YEARLY_INCOME_TABLE = [
    [0, 180000],
    [180000.01, 360000],
    [360000.01, 720000],
    [720000.01, 1800000],
    [1800000.01, 3600000],
    [3600000.01, 4800000]
]
INTERNACIONAL_WORK_TAXES = ["irpj", "csll", "cpp"]
ATTACH_3 = [
    {"total": 0.06, "deduct": 0,
        "taxes": {"cpp": 0.4340, "iss": 0.335, "csll": 0.035, "irpj": 0.04, "cofins":0.128, "pis/pasep": 0.0278}
    },
    {"total": 0.112, "deduct": 9360,
        "taxes": {"cpp": 0.4340, "iss": 0.32, "csll": 0.035, "irpj": 0.04, "cofins":0.128, "pis/pasep": 0.0305}
    },
    {"total": 0.135, "deduct": 17640,
        "taxes": {"cpp": 0.4340, "iss": 0.325, "csll": 0.035, "irpj": 0.04, "cofins":0.128, "pis/pasep": 0.0296}
    },
    {"total": 0.16, "deduct": 35640,
        "taxes": {"cpp": 0.4340, "iss": 0.325, "csll": 0.035, "irpj": 0.04, "cofins":0.128, "pis/pasep": 0.0296}
        },
    {"total": 0.21, "deduct": 125640,
        "taxes": {"cpp": 0.4340, "iss": 0.335, "csll": 0.035, "irpj": 0.04, "cofins":0.128, "pis/pasep": 0.0278}
        },
    {"total": 0.33, "deduct": 648000,
        "taxes": {"cpp": 0.4340, "iss": 0, "csll": 0.15, "irpj": 0.35, "cofins":0.1603, "pis/pasep": 0.0347}
    }
]
ATTACH_5 = [
    {"total": 0.155, "deduct": 0, 
        "taxes": {"cpp": 0.2885, "iss": 0.14, "csll": 0.15, "irpj": 0.25, "cofins":0.141, "pis/pasep": 0.0305}
    },
    {"total": 0.18, "deduct": 4500,
        "taxes": {"cpp": 0.2785, "iss": 0.17, "csll": 0.15, "irpj": 0.23, "cofins":0.141, "pis/pasep": 0.0305}
    },
    {"total": 0.195, "deduct": 9900,
        "taxes": {"cpp": 0.2385, "iss": 0.19, "csll": 0.15, "irpj": 0.24, "cofins":0.1492, "pis/pasep": 0.0323}
    },
    {"total": 0.205, "deduct": 17100,
        "taxes": {"cpp": 0.2385, "iss": 0.21, "csll": 0.15, "irpj": 0.21, "cofins":0.1574, "pis/pasep": 0.0341}
    },
    {"total": 0.23, "deduct": 62100,
        "taxes": {"cpp": 0.2385, "iss": 0.235, "csll": 0.125, "irpj": 0.23, "cofins":0.141, "pis/pasep": 0.0305}
    },
    {"total": 0.305, "deduct": 540000,
        "taxes": {"cpp": 0.295, "iss": 0, "csll": 0.155, "irpj": 0.35, "cofins":0.1644, "pis/pasep": 0.0356}
    }
]
R_FACTOR_THRESHOLD = 0.28


def get_pf_inss_cut(monthly_income: float) -> float:
    """

    Args:
        monthly_income (float): the person's monthly income

    Returns:
        float: inss cut, in the range [0, 1]
    """
    range_index = len(INSS_TABLE) -1
    for index, income_range in enumerate(INSS_TABLE):
        if income_range["start"] <= monthly_income <= income_range["end"]:
            range_index = index
            break
    return INSS_TABLE[range_index]["tax"]


def get_pf_irpf_cut(monthly_income: float) -> float:
    """

    Args:
        monthly_income (float): the person's monthly income

    Returns:
        float: taxes cut, in the range [0, 1]
        float: deduct value
    """
    range_index = 0
    for index, income_range in enumerate(IRRF_TABLE):
        if income_range["start"] <= monthly_income <= income_range["end"]:
            range_index = index
            break
    return IRRF_TABLE[range_index]["tax"], IRRF_TABLE[range_index]["deduct"]


def get_pj_taxes_cut(last_12_months_income: float,
                     table_attach: list,
                     is_external: bool = True) -> tuple[float, float]:
    """Calculate the tax cut based on last 12 months income.

    Checks in the proper table attachment based on the last 12 months income
    and use that to calculate the taxes cut

    Args:
        last_12_months_income (float): the last 12 months income
        table_attach (list): the table attachment
        is_external (bool, optional): If the service is provided in other
            country. Defaults to True.
    Returns:
        float: taxes cut, in the range [0, 1]
        float: deduct value
    """
    range_index = 0
    for index, income_range in enumerate(YEARLY_INCOME_TABLE):
        if income_range[0] <= last_12_months_income <= income_range[1]:
            range_index = index
            break
    taxes_range = table_attach[range_index]
    if is_external:
        cut_sum = 0
        for tax in INTERNACIONAL_WORK_TAXES:
            cut_sum += taxes_range["taxes"][tax]
        taxes_cut = taxes_range["total"]*cut_sum
    else:
        taxes_cut = taxes_range["total"]
    return taxes_cut, taxes_range["deduct"]/12


def calculate_monthly_revenue(monthly_income: float,
                              last_12_months_income: float,
                              is_external: bool = True,
                              pf_income: float = 0) -> int:
    """Find which taxes table/attachment gives the smaller taxes and
       calculates the monthly revenue after all discounts

    Args:
        monthly_income (float): the monthly income
        last_12_months_income (float): last 12 months total income
        is_external (bool, optional): If the service is provided in other
            country. Defaults to True.
        pf_income (float, optional): Income as PF (not PJ). Defaults to 0.
            If not given, the best value will ber calculated.

    Returns:
        float: the monthly revenue
        int: the table with the smaller taxes
    """
    ## Calculates using attachment 3
    pf_income_3 =  pf_income if pf_income else monthly_income*R_FACTOR_THRESHOLD
    inss_3 = get_pf_inss_cut(pf_income_3)
    irpf_3, deduct_3 = get_pf_irpf_cut(monthly_income*R_FACTOR_THRESHOLD)
    pf_discounts_3 = pf_income_3*(irpf_3) - deduct_3 + inss_3
    pf_discounted_3 = pf_income_3 - pf_discounts_3
    pj_taxes_3, pj_deduct_3 = get_pj_taxes_cut(last_12_months_income,
                                               ATTACH_3,
                                               is_external=is_external)
    discounted_income_3 = monthly_income -pf_income_3 \
                          - monthly_income*pj_taxes_3 + pf_discounted_3 \
                          + pj_deduct_3

    ## Calculates using attachment 5
    pf_income_3 =  pf_income if pf_income else monthly_income*R_FACTOR_THRESHOLD
    pf_income_5 = pf_income if pf_income else MININUM_WAGE
    inss_5 = get_pf_inss_cut(pf_income_5)
    irpf_5, deduct_5 = get_pf_irpf_cut(pf_income_5)
    pf_discounts_5 = pf_income_5*(irpf_5) - deduct_5 + inss_5
    pf_discounted_5 = pf_income_5 - pf_discounts_5
    pj_taxes_5, pj_deduct_5 = get_pj_taxes_cut(yearly_income, ATTACH_5,
                                               is_external=is_external)
    discounted_income_5 = monthly_income - pf_income_5 \
                          - monthly_income*pj_taxes_5 + pf_discounted_5 \
                          + pj_deduct_5

    ## return the greatest value
    return max(discounted_income_3, discounted_income_5)
