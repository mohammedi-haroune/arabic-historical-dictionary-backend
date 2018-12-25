
#!/usr/bin/env bash
echo -e "\e[36mPULLING BACKEND REPO\e[0m"
git pull
echo -e "\e[36mBUILDING BACKEND IMAGE\e[0m"
docker build -t gcr.io/arabic-historical-dictionary/tal-backend-us .
echo -e "\e[36mPUSHING BACKEND IMAGE\e[0m"
docker push gcr.io/arabic-historical-dictionary/tal-backend-us
echo -e "\e[36mCREATING credentials.json FILE\e[0m"
kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json
echo -e "\e[36mCREATING username AND password SERCRETS\e[0m"
kubectl create secret generic cloudsql --from-literal=username=tal --from-literal=password=tal
echo -e "\e[36mGOING TO FRONTEND\e[0m"
cd ../frontend/
echo -e "\e[36mEXCECUTING FRONTEND deploy.sh\e[0m"
bash deploy.sh
