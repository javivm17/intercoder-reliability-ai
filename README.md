# 🚀 LLM-Based Data Classification with Intercoder Reliability 🚀

## Overview

This repository contains a proof-of-concept implementation that adapts the traditional **intercoder reliability** technique for use with **Large Language Models (LLMs)**. The project leverages the **Cohen’s Kappa** coefficient to measure the agreement between the model and a human user during a calibration phase, with the goal of achieving consistent and reliable data classification.

## Key Features

- **Intercoder Reliability with LLM**: Utilizes the Cohen’s Kappa coefficient to align an LLM with human-provided labels.
- **Human-in-the-Loop**: Allows for user interaction during the calibration process, where the user provides feedback on model errors.
- **Abstract Learning**: The LLM extracts general, abstract lessons from user feedback to avoid overfitting and improve future predictions.
- **LangGraph Integration**: Implements the workflow using LangGraph, a framework for orchestrating and managing AI workflows.

## How It Works

1. **Initial Prediction**: The LLM predicts labels for 20% of the dataset.
2. **Comparison & Calculation**: These predictions are compared with the user-provided labels, and the Cohen’s Kappa coefficient is calculated.
3. **User Feedback**: If the Kappa coefficient is below 0.6, the user provides feedback on the incorrect predictions.
4. **Model Adjustment**: The model extracts lessons from this feedback and refines its predictions.
5. **Repetition**: Steps 1-4 are repeated until the Kappa coefficient exceeds 0.6.
6. **Final Prediction**: Once the threshold is met, the LLM labels the remaining 80% of the data.


### Example Data

The repository includes a small sample dataset for demonstration purposes.

## Limitations

This is a basic implementation designed to showcase the concept. The following areas may require further development:

- **Scalability**: Adjustments might be needed for larger datasets.
- **Model Customization**: The LLM's adaptability to different domains may vary.
- **Feedback Integration**: More sophisticated methods of feedback incorporation could enhance performance.

## ⚙ Getting Started

This guide will help you set up and deploy the LLM-Based Data Classification with Intercoder Reliability project.

#### 1. **Clone the Repository**

First, clone the repository to your local machine:

```bash
git clone https://github.com/javivm17/intercoder-reliability-ai.git
cd intercoder-reliability-ai
```

#### 2. **Run the installation script**

- Windows:

```PowerShell
.\setup.ps1
```

- Linux/Mac:

```bash
./setup.sh
```

#### 3. **Classify the Data**

> [!NOTE]
> In order to run this project correctly, you must tag some examples from the dataset. To do this, go to `/example_data/utils.py` and fill in the list of training labels.

#### 4. **Run the Project**

```bash
python app.py
```

## Contributing

Feel free to fork the repository and submit pull requests. Suggestions and improvements are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

Special thanks to the developers of LangGraph and the broader AI community for the tools and inspiration behind this project.

## Contact

For questions or suggestions, feel free to reach out via GitHub issues.

---

**Disclaimer**: This repository is a demo and should be considered as a starting point. Further refinement and exploration are encouraged to fully leverage the potential of this approach.
