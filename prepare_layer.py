# build_layers_docker.py
import os
import subprocess
import shutil
import sys
import locale

def run_command(cmd, description):
    """Run a command and handle errors gracefully with proper encoding"""
    print(f"🔄 {description}...")
    try:
        # Get system encoding, fallback to utf-8
        encoding = locale.getpreferredencoding() or 'utf-8'
        
        # On Windows, use utf-8 for Docker commands to avoid encoding issues
        if os.name == 'nt':
            encoding = 'utf-8'
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding=encoding,
            errors='replace'  # Replace problematic characters
        )
        
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(f"📋 Output: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except UnicodeDecodeError as e:
        print(f"❌ {description} failed due to encoding issue: {e}")
        print("Trying alternative approach...")
        return run_command_alternative(cmd, description)
    return True

def run_command_alternative(cmd, description):
    """Alternative command runner without capturing output"""
    print(f"🔄 {description} (alternative method)...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with return code: {e.returncode}")
        return False

def check_docker():
    """Check if Docker is available and running"""
    print("🐳 Checking Docker availability...")
    try:
        result = subprocess.run(
            "docker --version", 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(f"✅ Docker found: {result.stdout.strip()}")
        
        # Check if Docker daemon is running
        subprocess.run(
            "docker info", 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print("✅ Docker daemon is running")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker is not available or not running")
        print("Please make sure Docker Desktop is installed and running")
        return False
    except UnicodeDecodeError:
        print("⚠️ Docker found but with encoding issues, continuing...")
        return True

def build_layers_with_docker():
    """Build both layers using Docker"""
    
    # Check if Docker is available
    if not check_docker():
        return False
    
    container_name = "temp-layer-container"
    image_name = "lambda-layer-builder"
    
    try:
        # Clean up any existing container/image
        print("🧹 Cleaning up existing containers and images...")
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker rmi -f {image_name}", shell=True, capture_output=True)
        
        # Build the Docker image with progress output
        print("🔨 Building Docker image (this may take a few minutes)...")
        print("📋 Running: docker build -f Dockerfile.layer -t lambda-layer-builder .")
        
        # Use alternative method for building to avoid encoding issues
        if not run_command_alternative(
            f"docker build -f Dockerfile.layer -t {image_name} .",
            "Building Docker image"
        ):
            print("❌ Docker build failed. Let's try with verbose output...")
            # Try with no-cache to see detailed output
            return run_command_alternative(
                f"docker build --no-cache -f Dockerfile.layer -t {image_name} .",
                "Building Docker image (no cache)"
            )
        
        # Create container
        if not run_command_alternative(
            f"docker create --name {container_name} {image_name}",
            "Creating temporary container"
        ):
            return False
        
        # Remove existing layers
        print("📁 Removing existing layer directories...")
        if os.path.exists("ml_layer/python"):
            shutil.rmtree("ml_layer/python")
            print("✅ Removed existing ml_layer/python")
        if os.path.exists("upload_layer/python"):
            shutil.rmtree("upload_layer/python")
            print("✅ Removed existing upload_layer/python")
        
        # Extract ML layer
        print("📦 Extracting ML layer...")
        os.makedirs("ml_layer", exist_ok=True)
        if not run_command_alternative(
            f"docker cp {container_name}:/opt/ml_layer/python ml_layer/",
            "Extracting ML layer"
        ):
            return False
        
        # Extract upload layer
        print("📦 Extracting upload layer...")
        os.makedirs("upload_layer", exist_ok=True)
        if not run_command_alternative(
            f"docker cp {container_name}:/opt/upload_layer/python upload_layer/",
            "Extracting upload layer"
        ):
            return False
        
        # Run verification inside container
        print("🔍 Running verification...")
        if not run_command_alternative(
            f"docker run --rm {image_name}",
            "Verifying installations"
        ):
            print("⚠️ Verification failed, but layers may still work")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        print("🗑️ Temporary container removed")

def verify_local_layers():
    """Verify that the extracted layers work locally"""
    print("🔍 Verifying extracted layers locally...")
    
    # Check ML layer
    ml_layer_path = os.path.abspath("ml_layer/python")
    if os.path.exists(ml_layer_path):
        print(f"📁 ML layer found at: {ml_layer_path}")
        # Check for key files
        key_packages = ["langchain_core", "langchain_openai", "openai"]
        for pkg in key_packages:
            pkg_path = os.path.join(ml_layer_path, pkg)
            if os.path.exists(pkg_path):
                print(f"✅ Found package: {pkg}")
            else:
                print(f"⚠️ Package not found: {pkg}")
    else:
        print("❌ ML layer directory not found")
    
    # Check upload layer
    upload_layer_path = os.path.abspath("upload_layer/python")
    if os.path.exists(upload_layer_path):
        print(f"📁 Upload layer found at: {upload_layer_path}")
        # Check for PyPDF2
        pypdf_path = os.path.join(upload_layer_path, "PyPDF2")
        if os.path.exists(pypdf_path):
            print("✅ Found package: PyPDF2")
        else:
            print("⚠️ Package not found: PyPDF2")
    else:
        print("❌ Upload layer directory not found")

def check_requirements_files():
    """Check if requirements files exist and show their contents"""
    print("📋 Checking requirements files...")
    
    required_files = ["ml_layer-requirements.txt", "upload_layer-requirements.txt", "Dockerfile.layer"]
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
            if file.endswith(".txt"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            print(f"   📝 Contents:\n   {content.replace(chr(10), chr(10) + '   ')}")
                        else:
                            print("   ⚠️ File is empty")
                except Exception as e:
                    print(f"   ❌ Error reading file: {e}")
        else:
            print(f"❌ Missing: {file}")
            all_exist = False
    
    return all_exist

def main():
    print("🚀 Starting Docker-based layer build process...")
    print("="*60)
    
    # Check requirements files
    if not check_requirements_files():
        print("❌ Missing required files. Please ensure all files exist.")
        return False
    
    # Build layers
    if build_layers_with_docker():
        print("\n" + "="*60)
        print("🎉 Layers built successfully with Docker!")
        
        # Verify locally
        verify_local_layers()
        
        print("\n💡 Next steps:")
        print("   1. Run: sam build")
        print("   2. Run: sam deploy")
        print("   3. Test your Lambda function")
        
        return True
    else:
        print("\n❌ Layer build failed")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure Docker Desktop is running")
        print("   2. Try running: docker system prune -f")
        print("   3. Check if requirements files have valid package names")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)