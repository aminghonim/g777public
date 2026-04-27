from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

CLERK_PUBLISHABLE_KEY = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    if not CLERK_PUBLISHABLE_KEY:
        return """
        <html>
            <body style='font-family: Arial; padding: 50px; text-align: center;'>
                <h1 style='color: red;'>⚠️ Clerk Publishable Key Missing</h1>
                <p>Please add <b>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</b> to your .env file.</p>
            </body>
        </html>
        """
    
    template = """
    <html>
        <head>
            <title>G777 - Secure Login</title>
            <script src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js" defer></script>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: white;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                .card {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Welcome to G777</h1>
                <p>Securely log in to your account</p>
                <div id="clerk-app"></div>
            </div>

            <script>
                async function initClerk() {
                    const clerk = new Clerk('CLERK_PUBLISHABLE_KEY');
                    await clerk.load();

                    if (clerk.user) {
                        document.getElementById('clerk-app').innerHTML = `
                            <p>Logged in as: <b>${clerk.user.primaryEmailAddress.emailAddress}</b></p>
                            <button onclick="window.location.href='/api/docs'" style="padding: 10px 20px; border-radius: 5px; border: none; background: #4ecca3; color: white; cursor: pointer;">Go to Dashboard</button>
                        `;
                    } else {
                        clerk.mountSignIn(document.getElementById('clerk-app'));
                    }
                }

                window.addEventListener('load', initClerk);
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=template.replace("CLERK_PUBLISHABLE_KEY", CLERK_PUBLISHABLE_KEY))
