library(shiny)

shinyUI(pageWithSidebar(
  headerPanel("Williams Search Task: Trial Visualizer"),
  sidebarPanel(
    fileInput("archive", "Log Archive:", multiple=FALSE),
    uiOutput("trials")
  ),
  mainPanel(
    plotOutput("fixationplot", width = "900px", height = "900px"),
    conditionalPanel(
      condition = "input.trial",
      uiOutput("time_range_slider")
    )
  )
))