library(shiny)

shinyUI(pageWithSidebar(
  headerPanel("Williams Search Task: Trial Visualizer"),
  sidebarPanel(
    wellPanel(
      fileInput("archive", "Log Archive:", multiple=FALSE),
      uiOutput("trials")
    ),
    conditionalPanel(
      condition = "input.trial",
      wellPanel(
        checkboxInput("showSamples", "Show Eye Samples", value=TRUE),
        checkboxInput("showFixations", "Show Fixations", value=TRUE),
        checkboxInput("showMouse", "Show Mouse", value=TRUE)
      )
    )
  ),
  mainPanel(
    plotOutput("fixationplot", width="750px", height="750px")
  )
))