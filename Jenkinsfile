pipeline {
    agent any
    parameters {
    choice(
      name: 'Env',
      choices: ['Cloudzenix&Devsbx', 'Opssbx'],
      description: 'Passing the Environment'
    )
  }

    environment {
        BRANCH_NAME     = "${env.BRANCH_NAME}"
        AWS_DEFAULT_REGION = 'us-east-1'
        POLL_INTERVAL = 1000
        DURATION = 3600
        ROLE_NAME = 'Jenkins-deployer-role'
        STACK_NAME = 'iam-test-event-name'
        TEMPLATE_FILE = 'public_ssh_revoke.yaml'
        PROJECT_NAME = 'Public_SSH_Revoke'
        ARTEFACT_BUCKET_NAME = credentials('artefact-bucket-name')
    }

    stages {
       stage('checkout'){
            steps{
                git credentialsId: 'MY_BB_CRED', url: 'https://SreekantReddy@bitbucket.org/cloudzenix/public_ssh_revoke.git'
            }
       }
        stage('Build') {
            steps {
                withCredentials([string(credentialsId: 'artefact-bucket-name', variable: 'ARTEFACT_BUCKET_NAME')
                ]) {

                    withAWS(region:"${AWS_DEFAULT_REGION}") {
                        s3Upload(file:"${TEMPLATE_FILE}", bucket:"${env.ARTEFACT_BUCKET_NAME}", path:'template/')
                            script {
                            sh """
                                aws cloudformation validate-template --template-url \
                                https://${env.ARTEFACT_BUCKET_NAME}.s3.${AWS_DEFAULT_REGION}.amazonaws.com/template/${TEMPLATE_FILE}
                            """
                            }
                    }
                }
            }
        }
        stage('validate'){
            steps {
                withCredentials([string(credentialsId: 'artefact-bucket-name', variable: 'ARTEFACT_BUCKET_NAME')
                ]) {

                    script {
                        sh """
                            aws cloudformation package --template-file ${TEMPLATE_FILE} --s3-bucket ${ARTEFACT_BUCKET_NAME} \
                            --s3-prefix package --output-template-file package.yaml
                            aws s3 cp package.yaml s3://${ARTEFACT_BUCKET_NAME}/package/package.yaml
                        """
                    }
                }
            }
        }
        stage('Deploy to Cloudzenix'){
            when {
                expression { "${params.Env}" == 'Cloudzenix&Devsbx' }
                 }
            steps {
                echo "${BRANCH_NAME}"
                script {
                        cfnUpdater('978322299160')
                }
            }
        }
        stage('Deploy to Devsbx'){
            when {
                expression { "${params.Env}" == 'Cloudzenix&Devsbx' }
                 }
            steps {
                echo "${BRANCH_NAME}"
                script {
                        cfnUpdater('459602490943')
                }
            }
        }
        stage('Deploy to Opssbx'){
            when {
                expression { "${params.Env}" == 'Opssbx' }
                 }
            steps {
                echo "${BRANCH_NAME}"
                script {
                        OwncfnUpdater('602011150591')
                }
            }
        }   
    }
}
def cfnUpdater(account_id) {  
        
    withCredentials([string(credentialsId: 'artefact-bucket-name', variable: 'ARTEFACT_BUCKET_NAME')
        ]) {
        echo "account_id " + account_id
        withAWS(role:"${ROLE_NAME}", roleAccount:"${account_id}") {
            cfnUpdate(stack:"${STACK_NAME}", url:"https://s3.amazonaws.com/${ARTEFACT_BUCKET_NAME}/package/package.yaml")
        }
    }
}
def OwncfnUpdater(account_id) {  
        
    withCredentials([string(credentialsId: 'artefact-bucket-name', variable: 'ARTEFACT_BUCKET_NAME')
        ]) {
        echo "account_id " + account_id
        print("Hello from Opssbx")
            cfnUpdate(stack:"${STACK_NAME}", url:"https://s3.amazonaws.com/${ARTEFACT_BUCKET_NAME}/package/package.yaml")
    }
}

