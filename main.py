import pandas as pd
import numpy as np
import requests
import os


if __name__ == '__main__':

    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if ('A_office_data.xml' not in os.listdir('../Data') and
        'B_office_data.xml' not in os.listdir('../Data') and
        'hr_data.xml' not in os.listdir('../Data')):
        print('A_office_data loading.')
        url = "https://www.dropbox.com/s/jpeknyzx57c4jb2/A_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/A_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('B_office_data loading.')
        url = "https://www.dropbox.com/s/hea0tbhir64u9t5/B_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/B_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('hr_data loading.')
        url = "https://www.dropbox.com/s/u6jzqqg1byajy0s/hr_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/hr_data.xml', 'wb').write(r.content)
        print('Loaded.')


office_b_df = pd.read_xml('C:\\Users\\mikol\\Downloads\\B_office_data.xml')
office_a_df = pd.read_xml('C:\\Users\\mikol\\Downloads\\A_office_data.xml')
hr_df = pd.read_xml('C:\\Users\\mikol\\Downloads\\hr_data.xml')

hr_df = hr_df.set_index("employee_id")

A_office_IDs = office_a_df['employee_office_id'].tolist()
B_office_IDs = office_b_df['employee_office_id'].tolist()
for x in range(len(A_office_IDs)):
    A_office_IDs[x] = "A" + str(A_office_IDs[x])
for x in range(len(B_office_IDs)):
    B_office_IDs[x] = "B" + str(B_office_IDs[x])

office_a_df = office_a_df.set_index(pd.Index(A_office_IDs))
office_b_df = office_b_df.set_index(pd.Index(B_office_IDs))



offices_df = pd.concat([office_a_df, office_b_df], axis = 0)
merged_df = pd.merge(offices_df, hr_df, left_index=True, right_index=True, how='left', indicator=True)
merged_df = merged_df[merged_df['_merge'] == 'both']


merged_df = merged_df.drop(['employee_office_id', '_merge'], axis=1)
merged_df.sort_index(inplace=True)

print(merged_df.index.tolist())
print(merged_df.columns.tolist())



ans_1_df = merged_df.sort_values('average_monthly_hours', ascending=False)['Department']
ans_1 = ans_1_df[0:10].values.tolist()
print(ans_1)
ans_2 = merged_df[(merged_df['salary'] == 'low') & (merged_df['Department'] == "IT")]['number_project'].tolist()
ans_2 = sum(ans_2)
print(f"{ans_2}")
df_ans_3 = merged_df.loc[['A4', 'B7064', 'A3033'], ['last_evaluation', 'satisfaction_level']]
ans_3 = df_ans_3.values.tolist()
print(ans_3)


def count_bigger_5(series):
    c = 0
    for e in series:
        if e > 5:
            c += 1
    return c



grouped_df = merged_df.groupby('left').agg({
    'number_project': ['median', count_bigger_5],
    'time_spend_company': ['mean', 'median'],
    'Work_accident': 'mean',
    'last_evaluation': ['mean', 'std']
})
df_dict = grouped_df.round(2).to_dict()
print(df_dict)
                         
 
median_hours_df = merged_df.pivot_table(index='Department', columns=['left', 'salary'], values='average_monthly_hours', aggfunc='median')
filtered_pivot_df = median_hours_df.loc[median_hours_df[(0, 'high')] < median_hours_df[(0, 'medium')]]
filtered_pivot_df_2 = median_hours_df.loc[median_hours_df[(1, 'high')] > median_hours_df[(1, 'low')]]
pivot_df = pd.concat([filtered_pivot_df, filtered_pivot_df_2], axis=0)
print(pivot_df.round(2).to_dict())
promotion_df = merged_df.pivot_table(index='time_spend_company', columns=['promotion_last_5years'], values=['satisfaction_level', 'last_evaluation'], aggfunc=[min, max, 'mean'])
filtered_pivot_df_3 = promotion_df.loc[promotion_df[('mean', 'last_evaluation')][0] > promotion_df[('mean', 'last_evaluation')][1]]
print(filtered_pivot_df_3.round(2).to_dict())

