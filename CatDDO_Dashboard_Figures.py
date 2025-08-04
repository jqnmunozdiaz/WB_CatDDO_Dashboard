# %%
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Import files
data_dir = 'C:/Users/jqnmu/OneDrive/World_Bank_DRM/Review_CatDDOs/Dashboard/Data/'
CatDDO_data = data_dir + 'Cat_DDO_Portfolio.csv'
PDOS = pd.read_csv(CatDDO_data)

PDOS = PDOS.loc[(PDOS['Status'] != 'Dropped')] # Filter out dropped operations
PDOS['Fiscal Year'] = PDOS['Fiscal Year'].str.replace('FY', '\'') # Change name of FY column values
PDOS.reset_index(inplace = True, drop = True)

# Convert columns that start with 'FY' to integers
fy_cols = [col for col in PDOS.columns if col.startswith('FY')]
fy_cols_years = [f'\'{x[2:4]}' for x in fy_cols]
PDOS[fy_cols] = PDOS[fy_cols].apply(pd.to_numeric).astype(float)

# Retrieve Metadata:
Cat_DDO_Metadata_file = data_dir + 'Cat_DDO_Metadata.csv'
CatDDO_Meta = pd.read_csv(Cat_DDO_Metadata_file, index_col='Key')
Month = CatDDO_Meta.loc['Update_Month', 'Value']
Year = CatDDO_Meta.loc['Update_Year', 'Value']
Last_FY = CatDDO_Meta.loc['Last_FY', 'Value']
index_last_FY = fy_cols.index(Last_FY + " Cat DDO Disb.") + 1  # Retrieve last FY to show in figures
fy_cols = fy_cols[:index_last_FY]  # Limit to last FY
fy_cols_years = fy_cols_years[:index_last_FY]  # Limit to last FY

#%%####################
### Produce Figures ###
#######################

# Calculate total disbursed amounts for Cat DDO
dft = PDOS.copy()

disb_ibrd = dft[dft['Source'] == 'IBRD'][fy_cols].sum() # Get disbursement data by fiscal year and source IBRD/IDA
disb_ida = dft[dft['Source'] == 'IDA'][fy_cols].sum()
fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
ax.bar(fy_cols, disb_ibrd, 0.8, label='IBRD', zorder=11)
ax.bar(fy_cols, disb_ida, 0.8, bottom=disb_ibrd, label='IDA', zorder=11)
ax.set_title('Cat DDO Disbursements by Fiscal Year and Source')
ax.set_xlabel('Fiscal Year')
ax.set_ylabel('Disbursement Amount')
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${int(x/1e6)}M'))
ax.set_xlim(-0.5, len(fy_cols)-0.5)
ax.set_xticks(fy_cols)
ax.set_xticklabels(fy_cols_years, rotation=0)
ax.yaxis.grid(True, alpha=0.3, zorder=10)
ax.legend(frameon=True, edgecolor='white', fontsize=13)
for i in range(len(fy_cols)): # Add value labels on top of stacked bars
    total = disb_ibrd.iloc[i] + disb_ida.iloc[i]
    if total > 0:  # Only show label if total value is greater than 0
        ax.text(i, total, f'${int(total/1e6)}M', ha='center', va='bottom', fontsize=9)

#%% Figure - Number of Cat DDOs by Region
dft = pd.crosstab(PDOS['Fiscal Year'], PDOS['Region'])
# Add manually a row for FY "'10" with 0 for all regions, which does not have a Cat DDO
dft.loc["'10"] = 0
dft = dft.sort_index()
fig, ax = plt.subplots(figsize=(8, 4), dpi = 300)
dft.plot(ax=ax, kind='bar', stacked=True, width = 0.6, zorder = 5)
ax.set_title('Number of Cat DDOs approved by Fiscal Year and Region')
ax.set_ylabel('')
ax.set_ylabel('Number of Cat DDOs', size = 11)
ax.set_xlabel('Fiscal Year', size = 11)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.tick_params(axis='x', which='both', length=0, labelsize=11)
ax.yaxis.get_major_locator().set_params(integer=True)
ax.yaxis.grid(True, alpha=0.3, zorder=0)
ax.tick_params(axis='y', which='both', length=4, labelsize=11)
ax.legend(frameon=True, edgecolor='white')

#%% Figure - Number of Cat DDOs per region
dft = pd.crosstab(PDOS['Region'], PDOS['Status'])
fig, ax = plt.subplots(figsize=(4, 4), dpi = 200)
bars = dft.plot(ax=ax, kind='bar', stacked=True, width = 0.7, zorder = 5)
ax.set_xlabel('')
ax.set_ylabel('Number of Cat DDOs', size = 11)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.yaxis.grid(True, alpha=0.3, zorder=0)
ax.set_title('Number of Cat DDOs by Status and Region')
ax.legend(fontsize=10, bbox_to_anchor=[1, 1.01], loc='upper right', frameon=True, edgecolor='white', title=None)
ax.yaxis.get_major_locator().set_params(integer=True)

#%% Figure - Operations by Global Practice & Standalone or Hybrid
dft = pd.crosstab(PDOS['Fiscal Year'], PDOS['Standalone/Mixed'])
# Add manually a row for FY "'10" with 0 for all regions, which does not have a Cat DDO
dft.loc["'10"] = 0
dft = dft.sort_index()
fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
ax = dft.plot(kind='bar', stacked=True, ax=ax, width=0.6, zorder = 10)
ax.set_ylabel('Number of Cat DDOs', size=12)
ax.set_xlabel('Fiscal Year', size=12)
ax.set_title('Number of Cat DDOs by type of operation')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.tick_params(axis='x', which='both', length=0, labelsize=8)
ax.tick_params(axis='y', which='both', length=4, labelsize=8)
ax.legend(loc='best', frameon=True, edgecolor='white', fontsize=10)
ax.yaxis.grid(True, alpha=0.3, zorder=0)
ax.yaxis.get_major_locator().set_params(integer=True)

#%% Table of disbursement/undisbursed by source

IBRD_Disbursed = PDOS.loc[PDOS['Status'].isin(['Active', 'Closed'])]['Disbursements - Cat DDO Cum. (IBRD)'].sum() / 1e6
IDA_Disbursed = PDOS.loc[PDOS['Status'].isin(['Active', 'Closed'])]['Disbursements - Cat DDO Cum. (IDA)'].sum() / 1e6
IBRD_Undisbursed = PDOS.loc[PDOS['Status'].isin(['Active'])]['CAT DDO Undisbursed (IBRD)'].sum() / 1e6
IDA_Undisbursed = PDOS.loc[PDOS['Status'].isin(['Active'])]['CAT DDO Undisbursed (IDA)'].sum() / 1e6
IBRD_Pipeline = PDOS.loc[PDOS['Status'].isin(['Pipeline']) & (PDOS['Source'] == 'IBRD')]['Commitment (Cat DDO only)'].sum() / 1e6
IDA_Pipeline = PDOS.loc[PDOS['Status'].isin(['Pipeline']) & (PDOS['Source'] == 'IDA')]['Commitment (Cat DDO only)'].sum() / 1e6

summary_df = pd.DataFrame({
    'Disbursed': [round(IBRD_Disbursed, 1), round(IDA_Disbursed, 1)],
    'Undisbursed': [round(IBRD_Undisbursed, 1), round(IDA_Undisbursed, 1)],
    'Pipeline': [round(IBRD_Pipeline, 1), round(IDA_Pipeline, 1)]
}, index=['IBRD', 'IDA'])
summary_df.loc['Total'] = summary_df.sum() # Add totals row
print(summary_df)

#%%#########
### TEXT ###
############

# Phrase 1
num_active_closed = len(PDOS[PDOS['Status'].isin(['Active', 'Closed'])])
num_unique_countries = PDOS[PDOS['Status'].isin(['Active', 'Closed'])]['Country'].nunique()
num_closed_operations = len(PDOS[PDOS['Status'] == 'Closed'])
num_pipeline_operations = len(PDOS[PDOS['Status'] == 'Pipeline'])
print(f'As of {Month}, {Year}, {num_active_closed} Cat DDOs have been approved in {num_unique_countries} countries, with {num_closed_operations} of these operations having already been closed. There are additional {num_pipeline_operations} Cat DDOs currently in the pipeline.')

# Phrase 2
dft = PDOS.loc[(PDOS['Status'].isin(['Active', 'Closed']))] # Filter out dropped and pipelineoperations
val = round(dft['Disbursements - Cat DDO Cum.'].sum() / 1e9, 1)  # Convert to billion
print(f'Cat DDOs have disbursed a total of US$ {val} billion')

# Phrase 3
dft = PDOS.loc[(PDOS['Status'].isin(['Active', 'Closed']))] # Filter out dropped and pipeline operations
IBRD_val = dft['Disbursements - Cat DDO Cum. (IBRD)'].sum() / 1e6  # Convert to million
IDA_val = dft['Disbursements - Cat DDO Cum. (IDA)'].sum() / 1e6  # Convert to million
total_val = IBRD_val + IDA_val
if IBRD_val > IDA_val:
    print(f'IBRD countries account for larger disbursed amounts ({round(IBRD_val/total_val*100,1)}% against {round(IDA_val/total_val*100,1)}% for IDA countries). There has been a notable increase in the use of Cat DDOs to support IDA countries since 2018.')
else:
    print(f'IDA countries account for larger disbursed amounts ({round(IDA_val/total_val*100,1)}% against {round(IBRD_val/total_val*100,1)}% for IBRD countries). There has been a notable increase in the use of Cat DDOs to support IDA countries since 2018.')    
    
# Phrase 4
dft = PDOS.loc[(PDOS['Status'].isin(['Active']))] # Filter out closed, dropped and pipeline operations
val = round(dft['CAT DDO Undisbursed'].sum() / 1e9, 1)  # Convert to billion
print(f'There is an undisbursed balance of US$ {val} billion available for responding to catastrophes including public health-related emergencies.')

# Phrase 5
dft = PDOS.loc[(PDOS['Status'].isin(['Active']))] # Filter out closed dropped and pipeline operations
dft = dft.groupby('Region')['CAT DDO Undisbursed'].sum() / 1e6  # Convert to million
dft.sort_values(ascending=False, inplace=True)
val1 = round(dft.iloc[0], 1)  # Largest undisbursed amount
val2 = round((dft.iloc[0] / dft.sum()) * 100, 1)  # Percentage of largest undisbursed amount
val3 = dft.index[0]  # Region with largest undisbursed amount
val4 = round(dft.iloc[1], 1)  # Second largest undisbursed amount
val5 = round((dft.iloc[1] / dft.sum()) * 100, 1)  # Percentage of second largest undisbursed amount
val6 = dft.index[1]  # Region with second largest undisbursed amount
print(f'Of the undisbursed amount, US$ {val1} million ({val2}%) is allocated to {val3} and US$ {val4} million ({val5}%) to {val6}.')

# Phrase 6: Operations in the Pipeline
temp_IDA = PDOS[(PDOS['Status'] == 'Pipeline') & (PDOS['Source'] == 'IDA')]
val1 = len(temp_IDA)
val2 = temp_IDA['Commitment (Cat DDO only)'].sum() / 1e6  # Total undisbursed for IDA in pipeline
temp_IBRD = PDOS[(PDOS['Status'] == 'Pipeline') & (PDOS['Source'] == 'IBRD')]
val3 = len(temp_IBRD)
val4 = temp_IBRD['Commitment (Cat DDO only)'].sum() / 1e6  # Total undisbursed for IBRD in pipeline
print(f'{val1} Cat DDOs totaling US$ {val2} million are under preparation in IDA countries, compared to {val3} operations amounting to US$ {val4} million for IBRD countries.')

# Phrase 7: Distribution of Cat DDOs by Global Department and Operation Type
dft = PDOS[(PDOS['Status'].isin(['Active', 'Closed'])) & (PDOS['Standalone/Mixed'] == 'Mixed')]
val1 = dft['Commitment (All = DPO + Cat DDO)'].sum() / 1e6
val2 = dft['Commitment (Cat DDO only)'].sum() / 1e6
print(f"Of the US$ {val1} million committed to DPOs that combine upfront budget support with the Cat DDO instrument, US$ {val2} million has been specifically allocated to the Cat DDO.")

#%%#######################################
### Figure and text Climate cobenefits ###
##########################################

# Get separate list for both figures
Cat_DDO_list = list(PDOS['P#'])
standalone_list = list(PDOS[PDOS['Standalone/Mixed'] == 'Standalone']['P#'])
mixed_list = list(PDOS[PDOS['Standalone/Mixed'] == 'Mixed']['P#'])
titles = ['Standalone Cat DDOs', 'Mixed Cat DDOs']

 # Import Climate Cobenefits data
dfccb_full = pd.read_csv(data_dir + 'Climate_cobenefits.csv')
dfccb_full = dfccb_full.loc[(dfccb_full['Project Assessed'] == 'Assessed') & (dfccb_full    ['Project ID'].isin(Cat_DDO_list))] # Filter relevant operations

# Preprocessing
for col in ['TN2: Net IDA/IBRD Adaptation ($M) ','TO6: Total IDA/IBRD Commitment ($M)', 'TN3: Net IDA/IBRD Mitigation ($M) ']:
    dfccb_full[col] = pd.to_numeric(dfccb_full[col].str.replace('-', '0').str.replace(',', ''))

# Create percentages
dfccb_full['Adaptation CCB %'] = 100 * dfccb_full['TN2: Net IDA/IBRD Adaptation ($M) '] / dfccb_full['TO6: Total IDA/IBRD Commitment ($M)'] 
dfccb_full['Mitigation CCB %'] = 100 * dfccb_full['TN3: Net IDA/IBRD Mitigation ($M) '] / dfccb_full['TO6: Total IDA/IBRD Commitment ($M)']
dfccb_full['Total CCB %'] = dfccb_full['Adaptation CCB %'] + dfccb_full['Mitigation CCB %']

for i, select_list in enumerate([standalone_list, mixed_list]):
    dfccb = dfccb_full.copy()
    dfccb = dfccb.loc[(dfccb['Project ID'].isin(select_list))] # Filter relevant operations
    dfccb['Fig_id'] = dfccb['Country']  + ' (' + dfccb['FY'] + ')' # Create id for the figure
    dfccb = dfccb.sort_values(by='FY', ascending = False)
    dfccb.reset_index(inplace = True)

    print(dfccb['Total CCB %'].mean())

    fig, ax = plt.subplots(figsize=(5, 8))
    ax.barh(dfccb['Fig_id'], dfccb['Adaptation CCB %'], label='Adaptation co-benefits', zorder=10)
    ax.barh(dfccb['Fig_id'], dfccb['Mitigation CCB %'], left=dfccb['Adaptation CCB %'], label='Mitigation co-benefits', zorder=10)
    ax.set_xlabel('Climate co-benefits %')
    ax.set_ylabel('')
    ax.set_title(titles[i], fontsize=14, pad=15, loc='left')
    ax.set_ylim(-0.5, len(dfccb)-0.5)
    ax.axvline(x=dfccb['Total CCB %'].mean(), color='green', alpha=0.5, zorder=1, linestyle='--', label='Average of total co-benefits')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    handles, labels = ax.get_legend_handles_labels() # Reorder the legend labels
    order = [1, 2, 0]  # Change this list to reorder the labels as desired
    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], fontsize = 12, ncols = 3, bbox_to_anchor=[1, -0.05], loc = 'upper right', frameon = False)
    ax.tick_params(axis='y', which='both', length=0)
    ax.xaxis.grid(True, alpha=0.3, zorder = 1)
            
#%% TEXT

val1 = dfccb_full['Total CCB %'].mean()
print(f'On average, Cat DDO financing achieves {round(val1)}% climate co-benefits, driven predominantly by adaptation.')

val2 = dfccb_full.loc[(dfccb_full['Project ID'].isin(standalone_list))]['Total CCB %'].mean()
print(f'When implemented as standalone contingent-financing operations, Cat DDOs are significantly more effective, achieving an average of {round(val2)}% climate co-benefits.')

val3 = dfccb_full.loc[(dfccb_full['Project ID'].isin(mixed_list))]['Total CCB %'].mean()
print(f'In comparison, operations attain only {round(val3)}% when integrating a Cat DDO into a DPO (“mixed DPO”) that combines upfront budget support with catastrophe-contingent financing.')

# %%
