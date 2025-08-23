#!/bin/bash

# 🐢 Local to Remote Turtle Monitor Deployment Script
# Pushes local changes to GitHub and deploys to remote turtle system

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REMOTE_USER="shrimp"
REMOTE_HOST="10.0.20.69"
REMOTE_PATH="/home/shrimp/turtx"
COMMIT_MESSAGE="Update turtle monitoring system"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check git status
check_git_status() {
    log_info "Checking git status..."
    
    if ! command_exists git; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Check if there are changes to commit
    if git diff-index --quiet HEAD --; then
        log_warning "No changes to commit"
        return 1
    else
        log_info "Changes detected, will commit and push"
        return 0
    fi
}

# Function to commit and push changes
commit_and_push() {
    log_info "Committing and pushing changes..."
    
    # Add all changes
    git add .
    
    # Commit with timestamp
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    COMMIT_MSG="${COMMIT_MESSAGE} - $(date +"%Y-%m-%d %H:%M:%S")"
    
    git commit -m "$COMMIT_MSG"
    log_success "Changes committed"
    
    # Push to remote
    git push origin main
    log_success "Changes pushed to GitHub"
}

# Function to deploy to remote system
deploy_to_remote() {
    log_info "Deploying to remote turtle system..."
    
    # Test SSH connection
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null; then
        log_error "Cannot connect to remote system ${REMOTE_USER}@${REMOTE_HOST}"
        log_error "Please ensure SSH keys are configured and the system is accessible"
        exit 1
    fi
    
    # Execute remote deployment
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << 'EOF'
        set -e
        
        # Color codes for remote output
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        BLUE='\033[0;34m'
        NC='\033[0m'
        
        log() {
            echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
        }
        
        log_success() {
            echo -e "${GREEN}✅ $1${NC}"
        }
        
        log_error() {
            echo -e "${RED}❌ $1${NC}"
        }
        
        log_info() {
            echo -e "${YELLOW}ℹ️  $1${NC}"
        }
        
        # Navigate to project directory or clone if it doesn't exist
        if [ ! -d "/home/shrimp/turtx" ]; then
            log_info "Project directory not found, cloning from GitHub..."
            cd /home/shrimp
            git clone https://github.com/jopey-woof/turtx.git
        fi
        
        cd /home/shrimp/turtx
        
        # Pull latest changes
        log_info "Pulling latest changes from GitHub..."
        git pull origin main
        
        # Check if turtle-monitor directory exists
        if [ ! -d "turtle-monitor" ]; then
            log_error "turtle-monitor directory not found"
            exit 1
        fi
        
        # Navigate to turtle-monitor and run deployment
        cd turtle-monitor/deployment
        
        # Make deployment script executable
        chmod +x deploy-turtle-api.sh
        
        # Run deployment
        log_info "Running turtle API deployment..."
        ./deploy-turtle-api.sh
        
        log_success "Remote deployment completed successfully!"
EOF
    
    log_success "Deployment to remote system completed!"
}

# Function to display deployment status
show_status() {
    log_info "Deployment Status:"
    echo "  Local Repository: $(pwd)"
    echo "  Remote System: ${REMOTE_USER}@${REMOTE_HOST}"
    echo "  Remote Path: ${REMOTE_PATH}"
    echo "  API URL: http://${REMOTE_HOST}:8000"
    echo ""
    log_info "To check the deployment:"
    echo "  SSH: ssh ${REMOTE_USER}@${REMOTE_HOST}"
    echo "  API Health: curl http://${REMOTE_HOST}:8000/api/health"
    echo "  Kiosk Display: http://${REMOTE_HOST}:8000"
}

# Main execution
main() {
    log_info "🐢 Starting Turtle Monitor Deployment"
    log_info "Local → GitHub → Remote deployment workflow"
    echo ""
    
    # Check git status
    if check_git_status; then
        # Commit and push changes
        commit_and_push
    else
        log_info "No local changes to commit, proceeding with remote deployment"
    fi
    
    # Deploy to remote system
    deploy_to_remote
    
    # Show status
    echo ""
    show_status
    
    log_success "🎉 Deployment workflow completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --status       Show deployment status only"
        echo "  --remote-only  Skip git operations, deploy to remote only"
        echo ""
        echo "Environment variables:"
        echo "  REMOTE_USER    Remote username (default: turtle)"
        echo "  REMOTE_HOST    Remote host IP (default: 10.0.20.69)"
        echo "  REMOTE_PATH    Remote project path (default: /home/turtle/turtx)"
        exit 0
        ;;
    --status)
        show_status
        exit 0
        ;;
    --remote-only)
        log_info "Remote-only deployment mode"
        deploy_to_remote
        show_status
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 