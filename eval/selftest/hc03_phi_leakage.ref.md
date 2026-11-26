```json
{"findings":[
  {"id":"LEAK-01","artifact":"log","field":"mrn","value_shape":"clear SYN-######","risk":"high","recommended_mask":"SYN-***441"},
  {"id":"LEAK-02","artifact":"api","field":"sql","value_shape":"email in query","risk":"high","recommended_mask":"omit sql / hash email"},
  {"id":"LEAK-03","artifact":"ui","field":"query.ssn","value_shape":"ssn in URL","risk":"high","recommended_mask":"do not put SSN in query"},
  {"id":"LEAK-04","artifact":"log","field":"Authorization","value_shape":"raw bearer token","risk":"high","recommended_mask":"redact token"}
],"clean":["CLEAN-01","CLEAN-02","CLEAN-03"]}
```
