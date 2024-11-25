# ttbzrs Million Dollar Advisor

An innovative desktop application that helps you make informed financial decisions after receiving a hypothetical million-dollar windfall. Using advanced AI technology, this app provides personalized guidance, investment suggestions, and risk analysis in an engaging, interactive format.

## 🌟 Key Features

- **AI-Powered Financial Advice**: Leverages Llama 3.2 for intelligent financial guidance
- **Interactive Chat Interface**: Modern, neon-themed UI built with CustomTkinter
- **Document Analysis**: Upload and analyze financial PDFs
- **Session Management**: Save and load conversation history
- **Real-time Formatting**: Automatic styling of financial terms and numbers
- **Keyboard Shortcuts**: Efficient navigation and control
- **Help System**: Comprehensive sliding help panel

## 🛠 Prerequisites

1. **Python**: Version 3.13 or higher
2. **Ollama**: Local AI model server
   - [Download Ollama](https://ollama.ai/download)
   - Windows users: Enable WSL2 first
   - [WSL2 Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install)
3. **Llama 3.2**: Large Language Model
4. **System Requirements**:
   - 8GB RAM minimum (16GB recommended)
   - 10GB free disk space
   - Windows 10/11, macOS, or Linux

## 📦 Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/TinsaeB/ttbzrs_millionaire.git
   cd ttbzrs_millionaire
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and Setup Ollama**:
   - After installing Ollama, open a terminal and run:
   ```bash
   ollama pull llama2
   ```
   - Wait for the model download to complete (~4GB)

4. **Start Ollama Server**:
   ```bash
   ollama serve
   ```
   - Keep this terminal open while using the application

## 🚀 Running the Application

1. **Start the Application**:
   ```bash
   python -m ttbzrs_millionaire.main
   ```

2. **First-Time Setup**:
   - The app will show a splash screen while initializing
   - Wait for the connection to Ollama to establish
   - The main interface will appear automatically

3. **Quick Start Guide**:
   - Press F1 or click the ❓ button for help
   - Type your financial questions in the chat
   - Use Ctrl+O to load financial documents
   - Save sessions with Ctrl+S

## ⌨️ Keyboard Shortcuts

- **Ctrl+N**: New Chat
- **Ctrl+S**: Save Session
- **Ctrl+O**: Load PDF
- **F1/Ctrl+H**: Toggle Help
- **Esc**: Close Help
- **Ctrl+Q**: Quit
- **Enter**: Send Message
- **Shift+Enter**: New Line

## 💡 Usage Tips

1. **Financial Planning**:
   - Start by describing your financial goals
   - Ask about investment strategies
   - Discuss risk management
   - Explore tax implications

2. **Document Analysis**:
   - Upload financial PDFs for AI analysis
   - Get insights on investment documents
   - Review financial statements

3. **Session Management**:
   - Save important conversations
   - Load previous sessions for reference
   - Start new chats for different scenarios

## 🎨 UI Features

- **Message Formatting**:
  - Currency: **$1,000**
  - Percentages: `7.5%`
  - Market terms: *bull market*
  - Risk levels: **high-risk**
  - Technical terms: `ETF`, `IRA`

- **Status Indicators**:
  - 🟢 Ready
  - 🤔 Thinking
  - ⏳ Processing
  - 🔴 Error

## 🔧 Troubleshooting

1. **Ollama Connection Issues**:
   - Ensure Ollama is running: `ollama serve`
   - Check WSL2 is running (Windows users)
   - Verify no firewall blocking

2. **Performance Issues**:
   - Close resource-heavy applications
   - Ensure sufficient free RAM
   - Check CPU usage

3. **UI Problems**:
   - Update CustomTkinter: `pip install --upgrade customtkinter`
   - Check Python version compatibility
   - Verify display resolution settings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 🙏 Acknowledgments

- Built with CustomTkinter
- Powered by Ollama and Llama 3.2
- Special thanks to the open-source community

---
*Note: This is a simulation tool for educational purposes. Always consult with qualified financial advisors for real investment decisions.*
