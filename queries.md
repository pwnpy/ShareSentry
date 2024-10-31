#### Database Connection Strings
(FileExtension:config OR FileExtension:xml OR FileExtension:json OR FileExtension:yml OR FileExtension:properties OR FileExtension:py) AND ((content:"connection string" AND content:"password" AND (content:"server=" OR content:"database=")) OR (content:"mongodb" AND content:"authSource" AND content:"password") OR (content:"cosmos" AND content:"primaryKey") OR (content:"redis" AND content:"password" AND content:"ssl") OR (content:"connect(" AND content:"password" AND content:"host") OR (content:"pymysql" AND content:"passwd")) AND NOT (content:"example" OR content:"test" OR content:"dummy" OR content:"local")

### Cloud Service Credentials with Context
(FileExtension:config OR FileExtension:yml OR FileExtension:properties OR FileExtension:env) AND ((content:"aws_access_key_id" AND content:"aws_secret_access_key") OR (content:"AZURE_CLIENT_ID" AND content:"AZURE_CLIENT_SECRET" AND content:"AZURE_TENANT_ID") OR (content:"GOOGLE_APPLICATION_CREDENTIALS" AND content:"project_id") OR (content:"service_account" AND content:"private_key" AND content:"client_email") OR (content:"managed_identity" AND content:"client_id" AND content:"resource_id")) AND NOT content:"template"

### API Keys, GraphQL and Authentication Configuration Files
(FileExtension:config OR FileExtension:json OR FileExtension:yml OR FileExtension:env) AND ((content:"api_key" AND content:"secret" AND NOT content:"dummy") OR (content:"bearer" AND content:"token" AND NOT content:"placeholder") OR (content:"graphql" AND content:"authorization" AND content:"header") OR (content:"apollo" AND content:"secret") OR (content:"authentication" AND content:"credentials" AND NOT content:"example") OR (content:"oauth" AND content:"client_secret" AND content:"client_id" AND NOT content:"placeholder")) AND NOT (content:"example" OR content:"test" OR content:"demo" OR content:"playground")

### Identity and SSO Configuration
(FileExtension:config OR FileExtension:json OR FileExtension:xml OR FileExtension:yml) AND ((content:"saml" AND content:"privateKey" AND content:"certificate") OR (content:"oauth" AND content:"client_secret" AND content:"redirect_uri") OR (content:"identity" AND content:"provider" AND content:"secret" AND content:"tenant") OR (content:"auth0" AND content:"client_secret")) AND NOT (content:"template" OR content:"example")

### Storage Account Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"DefaultEndpointsProtocol=https" AND content:"AccountKey=") OR (content:"BlobEndpoint" AND content:"SharedAccessSignature")) AND NOT content:"example"

### CI/CD Secrets
(FileExtension:yml OR FileExtension:yaml OR FileExtension:xml OR FileExtension:groovy OR FileExtension:jenkinsfile) AND ((content:"withCredentials" AND content:"usernamePassword") OR (content:"credentialsId" AND content:"secret") OR (content:"env:" AND content:"secrets.") OR (content:"github_token:" AND content:"${{") OR (content:"variables:" AND content:"group:" AND content:"key vault") OR (content:"secret:" AND content:"azureSubscription:")) AND NOT (content:"example" OR content:"template" OR content:"dummy")

### Docker and Kubernetes Secrets
(FileExtension:yml OR FileExtension:yaml) AND ((content:"kind: Secret" AND content:"data:" AND (content:"stringData:" OR content:"apiVersion:")) OR (content:"docker-compose" AND content:"environment:" AND (content:"MYSQL_ROOT_PASSWORD:" OR content:"POSTGRES_PASSWORD:")))

### Private Keys and Certificates
((content:"BEGIN PRIVATE KEY" AND content:"END PRIVATE KEY") OR (content:"BEGIN RSA PRIVATE KEY" AND content:"END RSA PRIVATE KEY") OR (content:"BEGIN CERTIFICATE" AND content:"END CERTIFICATE") OR (content:"ssh-rsa" OR content:"BEGIN OPENSSH PRIVATE KEY")) AND NOT content:"example"

### Email and Payment Gateway Configurations
(FileExtension:config OR FileExtension:env OR FileExtension:json OR FileExtension:yml) AND ((content:"smtp" AND content:"password" AND content:"host") OR (content:"sendgrid" AND content:"api_key") OR (content:"stripe" AND content:"secret_key" AND content:"publishable_key") OR (content:"paypal" AND content:"client_id" AND content:"client_secret")) AND NOT (content:"example" OR content:"test")

### ML, LLMs, and Data Pipeline Configurations
(FileExtension:yml OR FileExtension:json OR FileExtension:config) AND ((content:"openai" AND content:"api_key") OR (content:"api.openai.com" AND content:"key") OR (content:"anthropic" AND content:"key") OR (content:"huggingface" AND content:"token") OR (content:"tensorflow" AND content:"credentials") OR (content:"pipeline" AND content:"source" AND content:"credentials") OR (content:"dataflow" AND content:"secret" AND content:"connection")) AND NOT (content:"example" OR content:"test" OR content:"demo")

### PowerShell and SysAdmin Scripts
(FileExtension:ps1 OR FileExtension:sh OR FileExtension:py) AND ((content:"New-Object System.Management.Automation.PSCredential" AND content:"ConvertTo-SecureString") OR (content:"Invoke-Command" AND content:"credential" AND content:"-Password") OR (content:"backup" AND content:"password" AND (content:"server" OR content:"database"))) AND NOT (content:"example" OR content:"test" OR content:"dummy")

### Security Configurations Files
(FileExtension:config OR FileExtension:xml OR FileExtension:properties OR FileExtension:yml OR FileExtension:json) AND ((content:"encryption" AND content:"key" AND content:"algorithm" AND content:"provider") OR (content:"cipher" AND content:"secret" AND content:"mode") OR (content:"vulnerability" AND content:"api_key" AND content:"severity") OR (content:"scanner" AND content:"authentication" AND content:"token") OR (content:"jwt" AND content:"secret" AND content:"algorithm") OR (content:"JsonWebToken" AND content:"signing_key")) AND NOT (content:"example" OR content:"test" OR content:"demo" OR content:"template")

### VPN Configuration Files
(FileExtension:config OR FileExtension:ovpn OR FileExtension:conf) AND ((content:"remote" AND content:"auth-user-pass" AND NOT content:"example") OR (content:"cipher" AND content:"key-direction" AND content:"BEGIN CERTIFICATE"))

### Terraform State Files
(FileExtension:tf OR FileExtension:tfstate OR FileExtension:tfvars) AND (content:"resource" AND content:"sensitive" AND (content:"access_key" OR content:"secret_key"))
