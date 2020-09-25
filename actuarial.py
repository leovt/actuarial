import math
import pandas

contracts = pandas.read_excel('SampleInput.xlsx')

valdate = pandas.Timestamp('2020-10-01')

def month_diff(a, b):
    return 12 * (a.year - b.year) + (a.month - b.month)

def elapsed_months(record):
    return month_diff(valdate, record.StartDate)

def start_age_months(record):
    return month_diff(record.StartDate, record.BirthDate)

contracts['ElapsedMonths'] = contracts.apply(elapsed_months, 'columns')
contracts['StartAgeMonths'] = contracts.apply(start_age_months, 'columns')

print(contracts)

# time = pandas.DataFrame({'time':range(projection_max)})
#
# print(time)
#
# def product(df1, df2):
#     df1['__dummy_key'] = 0
#     df2['__dummy_key'] = 0
#     product = pandas.merge(df1, df2)
#     del product['__dummy_key']
#     return product
#
# projection = product(contracts, time)
#
# projection['age_months'] = projection['time'] + projection['ElapsedMonths'] + projection['StartAgeMonths']
#
# def mortality(record):
#     alpha = {'M': 1.7e-5, 'F': 1.5e-5}[record.Sex]
#     beta = 0.0081
#     return min(1.0, alpha * math.exp(record.age_months * beta))
#
# projection['MortalityRate'] = projection.apply(mortality, 'columns')
#
# def survivors(record):
#     global surv_value
#     if record.time == 0:
#         this = 1
#     else:
#         this = surv_value
#     surv_value = this * (1-record.MortalityRate)
#     return this
#
# projection['Survivors'] = projection.apply(survivors, 'columns')
# projection['cumsum'] = projection.groupby('ContractNo').time.cumsum()
#
#
# print(projection)

def project(record):
    alpha = {'M': 1.7e-5, 'F': 1.5e-5}[record.Sex]
    beta = 0.0081
    survivors = 1
    accum_deaths = 0

    Time = [0]
    AgeMonths = [record.StartAgeMonths]
    Survivors = [survivors]
    AccumDeaths = [accum_deaths]
    Deaths = [None]

    for t in range(record.TermMonths - record.ElapsedMonths + 1):
        age_months = record.StartAgeMonths + t
        # use mortality from previous month
        mortality = min(1.0, alpha * math.exp((age_months-1) * beta))
        deaths = survivors * mortality
        survivors -= deaths
        accum_deaths += deaths

        Time.append(t)
        AgeMonths.append(age_months)
        Survivors.append(survivors)
        AccumDeaths.append(accum_deaths)
        Deaths.append(deaths)

    return pandas.DataFrame({
        'ContractNo': [record.ContractNo]*len(Time),
        'Time': Time,
        'Survivors': Survivors,
        'AccumDeaths': AccumDeaths,
        'Deaths': Deaths,
        })


projections = contracts.apply(project, 'columns').tolist()
projection = pandas.concat(projections)
print(projection)
