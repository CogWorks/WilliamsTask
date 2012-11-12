library(shiny)

shinyUI(pageWithSidebar(
  headerPanel("Williams Search Task: Trial Visualizer"),
  sidebarPanel(
    fileInput("archive", "Log Archive:", multiple=FALSE),
    conditionalPanel(
      condition = "output.ntrials",
      uiOutput("trials")
    )
  ),
  mainPanel(
    plotOutput("fixationplot", width = "900px", height = "900px")
  )
))