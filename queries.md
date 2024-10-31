#### Database Connection Strings
(FileExtension:config OR FileExtension:xml OR FileExtension:json OR FileExtension:yml OR FileExtension:properties) AND (content:"connection string" AND content:"password" AND (content:"server=" OR content:"database="))

### Cloud Service Credentials with Context
(FileExtension:config OR FileExtension:yml OR FileExtension:properties OR FileExtension:env) AND ((content:"aws_access_key_id" AND content:"aws_secret_access_key") OR (content:"AZURE_CLIENT_ID" AND content:"AZURE_CLIENT_SECRET" AND content:"AZURE_TENANT_ID") OR(content:"GOOGLE_APPLICATION_CREDENTIALS" AND content:"project_id"))

### Authentication Configuration Files
(FileExtension:config OR FileExtension:xml OR FileExtension:json) AND ((content:"authentication" AND content:"credentials" AND NOT content:"example") OR (content:"oauth" AND content:"client_secret" AND content:"client_id" AND NOT content:"placeholder"))

### Kubernetes Secrets
(FileExtension:yml OR FileExtension:yaml) AND (content:"kind: Secret" AND content:"data:" AND (content:"stringData:" OR content:"apiVersion:"))

### Docker Compose with Secrets
(FileExtension:yml OR FileExtension:yaml) AND (content:"docker-compose" AND content:"environment:" AND (content:"MYSQL_ROOT_PASSWORD:" OR content:"POSTGRES_PASSWORD:"))

### Terraform State Files
(FileExtension:tf OR FileExtension:tfstate OR FileExtension:tfvars) AND (content:"resource" AND content:"sensitive" AND (content:"access_key" OR content:"secret_key"))

### API Keys in Configuration Files
(FileExtension:config OR FileExtension:json OR FileExtension:yml OR FileExtension:env) AND ((content:"api_key" AND content:"secret" AND NOT content:"dummy") OR (content:"bearer" AND content:"token" AND NOT content:"placeholder")) AND NOT content:"example"

### Email Service Configurations
(FileExtension:config OR FileExtension:env OR FileExtension:json) AND ((content:"smtp" AND content:"password" AND content:"host") OR(content:"sendgrid" AND content:"api_key" AND NOT content:"example"))

### Payment Gateway Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"stripe" AND content:"secret_key" AND content:"publishable_key") OR(content:"paypal" AND content:"client_id" AND content:"client_secret")) AND NOT content:"test"

### PowerShell Scripts with Credentials
FileExtension:ps1 AND ((content:"New-Object System.Management.Automation.PSCredential" AND content:"ConvertTo-SecureString") OR(content:"Invoke-Command" AND content:"credential" AND content:"-Password")) AND NOT content:"example"

### Python Scripts with Database Access
FileExtension:py AND ((content:"connect(" AND content:"password" AND content:"host") OR(content:"pymysql" AND content:"passwd" AND NOT content:"example")) AND NOT (content:"dummy" OR content:"test")

### Backup Scripts with Credentials
(FileExtension:ps1 OR FileExtension:sh OR FileExtension:py) AND (content:"backup" AND content:"password" AND (content:"server" OR content:"database")) AND NOT (content:"example" OR content:"test" OR content:"dummy")

### Private Keys and Certificates
((content:"BEGIN PRIVATE KEY" AND content:"END PRIVATE KEY") OR (content:"BEGIN RSA PRIVATE KEY" AND content:"END RSA PRIVATE KEY") OR (content:"BEGIN CERTIFICATE" AND content:"END CERTIFICATE")) AND NOT content:"example"

### SSH Keys
(FileExtension:pem OR FileExtension:key OR FileExtension:ppk) AND (content:"ssh-rsa" OR content:"BEGIN OPENSSH PRIVATE KEY")

### JWT Token Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"jwt" AND content:"secret" AND content:"algorithm") OR (content:"JsonWebToken" AND content:"signing_key" AND NOT content:"example")) AND NOT (content:"test" OR content:"demo")

### GraphQL API Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"graphql" AND content:"authorization" AND content:"header") OR (content:"apollo" AND content:"secret" AND NOT content:"example")) AND NOT content:"playground"

### Service Account Configurations
(FileExtension:json OR FileExtension:yml OR FileExtension:xml) AND ((content:"service_account" AND content:"private_key" AND content:"client_email") OR (content:"managed_identity" AND content:"client_id" AND content:"resource_id")) AND NOT content:"template"
### Jenkins Credentials
(FileExtension:xml OR FileExtension:groovy OR FileExtension:jenkinsfile) AND ((content:"withCredentials" AND content:"usernamePassword" AND NOT content:"example") OR (content:"credentialsId" AND content:"secret" AND NOT content:"dummy"))

### GitHub Actions Secrets
(FileExtension:yml OR FileExtension:yaml) AND ((content:"env:" AND content:"secrets." AND NOT content:"example") OR (content:"github_token:" AND content:"${{" AND NOT content:"template"))

### Azure DevOps Pipeline Variables
(FileExtension:yml OR FileExtension:yaml) AND ((content:"variables:" AND content:"group:" AND content:"key vault") OR (content:"secret:" AND content:"azureSubscription:" AND NOT content:"example"))

### Authentication Middleware Settings
(FileExtension:config OR FileExtension:json OR FileExtension:js) AND ((content:"middleware" AND content:"authentication" AND content:"secret") OR (content:"passport" AND content:"strategy" AND content:"clientSecret")) AND NOT (content:"example" OR content:"demo")

### SSO Integration Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:xml) AND ((content:"saml" AND content:"privateKey" AND content:"certificate") OR (content:"oauth" AND content:"client_secret" AND content:"redirect_uri")) AND NOT content:"template"

### Encryption Key Configurations
(FileExtension:config OR FileExtension:xml OR FileExtension:properties) AND ((content:"encryption" AND content:"key" AND content:"algorithm" AND content:"provider") OR (content:"cipher" AND content:"secret" AND content:"mode" AND NOT content:"example"))

### NoSQL Database Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"mongodb" AND content:"authSource" AND content:"password") OR (content:"cosmos" AND content:"primaryKey" AND NOT content:"example") OR (content:"redis" AND content:"password" AND content:"ssl")) AND NOT (content:"test" OR content:"local")

### Storage Account Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"DefaultEndpointsProtocol=https" AND content:"AccountKey=") OR (content:"BlobEndpoint" AND content:"SharedAccessSignature" AND NOT content:"example"))

### Backup Configuration Files
(FileExtension:config OR FileExtension:json OR FileExtension:xml) AND ((content:"backup" AND content:"encryption" AND content:"key" AND NOT content:"example") OR (content:"restore" AND content:"credentials" AND content:"source" AND NOT content:"test"))
### Security Scanner Configurations
(FileExtension:yml OR FileExtension:json OR FileExtension:xml) AND ((content:"vulnerability" AND content:"api_key" AND content:"severity") OR (content:"scanner" AND content:"authentication" AND content:"token")) AND NOT content:"template"

### Identity Provider Settings
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"identity" AND content:"provider" AND content:"secret" AND content:"tenant") OR (content:"auth0" AND content:"client_secret" AND NOT content:"example"))

### VPN Configuration Files
(FileExtension:config OR FileExtension:ovpn OR FileExtension:conf) AND ((content:"remote" AND content:"auth-user-pass" AND NOT content:"example") OR (content:"cipher" AND content:"key-direction" AND content:"BEGIN CERTIFICATE"))

### ML Model API Configurations
(FileExtension:yml OR FileExtension:json OR FileExtension:config) AND ((content:"openai" AND content:"api_key" AND NOT content:"example") OR (content:"api.openai.com" AND content:"key")OR (content:"anthropic" AND content:"key")OR (content:"huggingface" AND content:"token" AND NOT content:"demo") OR (content:"tensorflow" AND content:"credentials" AND NOT content:"test"))

### Data Pipeline Configurations
(FileExtension:config OR FileExtension:json OR FileExtension:yml) AND ((content:"pipeline" AND content:"source" AND content:"credentials" AND NOT content:"example") OR (content:"dataflow" AND content:"secret" AND content:"connection" AND NOT content:"test"))