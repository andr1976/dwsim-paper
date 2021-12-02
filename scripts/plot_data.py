import numpy as np
import pylab as plt
import numpy.ma as ma
import pandas as pd
import seaborn as sn
import statsmodels.formula.api as smf 

X_n=np.loadtxt("scaled_testplan.csv",delimiter=",")
Y_dwsim = np.loadtxt("DWSIM_results_cleaned.csv",delimiter=",")
Y_HYSYS = np.loadtxt("HYSYS_result.csv",delimiter=",")

dataset = pd.DataFrame({'DWSIM_liquid': Y_dwsim[:, 0], 'DWSIM_power': Y_dwsim[:, 1], 'DWSIM_rvp': Y_dwsim[:, 2], 'HYSYS_liquid': Y_HYSYS[:, 0], 'HYSYS_power': Y_HYSYS[:, 1], 'HYSYS_rvp': Y_HYSYS[:, 2]})
dataset.insert(0, "Tsep1", X_n[:,0], True)
dataset.insert(1, "Psep1", X_n[:,1], True)
dataset.insert(2, "Psep2", X_n[:,2], True)
dataset.insert(3, "Tsep3", X_n[:,3], True)
dataset.insert(4, "Psep3", X_n[:,4], True)
dataset.insert(5, "Tscu1", X_n[:,5], True)
dataset.insert(6, "Tscu2", X_n[:,6], True)
dataset.insert(7, "Tscu3", X_n[:,7], True)
dataset.insert(8, "Pbost", X_n[:,8], True)
dataset.insert(9, "Trefrig", X_n[:,9], True)
dataset_clean = dataset[dataset['DWSIM_liquid'] != -9999]

rmse=[]
nrmse=[]
rsquared=[]
rsquared_adj=[]

model = smf.ols('DWSIM_liquid ~ HYSYS_liquid', data=dataset_clean )
res=model.fit()
res.summary()
rmse.append(np.sqrt(res.mse_resid))
nrmse.append(rmse[-1]/dataset_clean['HYSYS_liquid'].mean())
rsquared.append(res.rsquared)
rsquared_adj.append(res.rsquared_adj)

ax = sn.regplot(x="HYSYS_liquid", y="DWSIM_liquid", truncate=False, data=dataset_clean, color = 'k')
ax.set_xlabel("HYSYS liquid export molar flow (kmole/h)")
ax.set_ylabel("DWSIM liquid export molar flow (kmole/h)")
fig = ax.get_figure()
fig.savefig("liquid_plot.png")
ax.clear()
fig.clear()

model = smf.ols('DWSIM_power ~ HYSYS_power', data=dataset_clean )
res=model.fit()
res.summary()
rmse.append(np.sqrt(res.mse_resid))
nrmse.append(rmse[-1]/dataset_clean['HYSYS_power'].mean())
rsquared.append(res.rsquared)
rsquared_adj.append(res.rsquared_adj)

ax = sn.regplot(x="HYSYS_power", y="DWSIM_power", truncate=False, data=dataset_clean, color = 'k')
ax.set_xlabel("HYSYS main power requirement (kW)")
ax.set_ylabel("DWSIM main power requirement (kW)")
fig = ax.get_figure()
fig.savefig("power.png")
ax.clear()
fig.clear()

model = smf.ols('DWSIM_rvp ~ HYSYS_rvp', data=dataset_clean )
res=model.fit()
res.summary()
rmse.append(np.sqrt(res.mse_resid))
nrmse.append(rmse[-1]/dataset_clean['HYSYS_rvp'].mean())
rsquared.append(res.rsquared)
rsquared_adj.append(res.rsquared_adj)


ax = sn.regplot(x="HYSYS_rvp", y="DWSIM_rvp", truncate=False, data=dataset_clean, color = 'k')
ax.set_xlabel("HYSYS liquid export RVP (psia)")
ax.set_ylabel("DWSIM liquid export RVP (psia)")
fig = ax.get_figure()
fig.savefig("rvp_plot.png")
ax.clear()
fig.clear()

sum_data = np.stack([["Liquid flow","Power","RVP"],rsquared,rsquared_adj,rmse,nrmse],axis=1)
cols=['Response','R**2','R**2(adjust)','RMSE','RMSE(normalised)']
sum_table = pd.DataFrame(data=sum_data,columns=cols)
print(sum_table.to_latex(index=False))
