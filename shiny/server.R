library(grid)
library(png)
library(latticeExtra)

library(shiny)

shinyServer(function(input, output) {
  
  archiveInfo <- reactive(function() {
    if (is.null(input$archive)) return(NULL)
    base <- head(unlist(strsplit(input$archive$name,"\\.")),1)
    untar(input$archive$datapath,exdir=tempdir(),extras="-m")
    ntrials <- length(list.files(paste(tempdir(),base,sep="/"),pattern="png$"))
    list(base=base,ntrials=ntrials)
  })
  
  trialData <- reactive(function() {
    if (is.null(input$trial)) return(NULL)
    ai <- archiveInfo()
    datafilename <- paste(tempdir(),ai$base,sprintf("trial-%02d.txt", as.numeric(input$trial)),sep="/")
    d <- subset(read.delim(datafilename),state=="SEARCH")
    rimg <- as.raster(readPNG(paste(tempdir(),ai$base,sprintf("trial-%02d.png", as.numeric(input$trial)),sep="/"),FALSE))
    rimg <- rimg[,315:1365]
    list(data=d,rimg=rimg)
  })
  
  output$trials <- reactiveUI(function() {
    ai <- archiveInfo()
    if (is.null(ai)) return(NULL)
    selectInput("trial", "Trial:", choices=1:ai$ntrials, selected=1)
  })
  
  basePlot <- reactive(function() {
    td <- trialData()
    if (is.null(td)) return(NULL)
    xyplot(smi_syl~smi_sxl,
      data=subset(td$data, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0),
      scales=list(draw=F), col="blue", type="b", aspect=1, ylab="",xlab="",
      ylim=c(0,1050), xlim=c(315,1365),
      panel=function(...) {
        grid.raster(td$rimg)
      }
    )
  })
  
  samplesPlot <- reactive(function() {
    td <- trialData()
    if (is.null(td)) return(NULL)
    xyplot(smi_syl~smi_sxl,
           data=subset(td$data, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0),
           scales=list(draw=F), col="blue", type="b", aspect=1, ylab="",xlab="",
           ylim=c(0,1050), xlim=c(315,1365), pch=16,
           panel=function(...) {
             panel.xyplot(...)
           }
    )
  })
  
  fixationsPlot <- reactive(function() {
    td <- trialData()
    if (is.null(td)) return(NULL)
    xyplot(smi_fy~smi_fx,data=subset(td$data, smi_type=="r"), col="red", pch=16, aspect=1, ylim=c(0,1050), xlim=c(315,1365),scales=list(draw=F))
  })
  
  mousePlot <- reactive(function() {
    td <- trialData()
    if (is.null(td)) return(NULL)
    xyplot(mouse_y~mouse_x,data=subset(td$data, event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET"), pch=16, type="b", col="green", aspect=1, ylim=c(0,1050), xlim=c(315,1365), scales=list(draw=F))
  })
  
  output$fixationplot <- reactivePlot(function() {
    p <- basePlot()
    if (is.null(p)) return(NULL)
    if (input$showSamples) p <- p + samplesPlot()
    if (input$showFixations) p <- p + fixationsPlot()
    if (input$showMouse) p <- p + mousePlot()
    print(p)
  })
  
})