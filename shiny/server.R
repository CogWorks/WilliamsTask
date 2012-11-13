library(grid)
library(png)
library(latticeExtra)

library(shiny)

shinyServer(function(input, output) {
  output$ntrials <- reactive(function() {
    if (is.null(input$archive)) {
      return(0)
    }
    base <- head(unlist(strsplit(input$archive$name,"\\.")),1)
    untar(input$archive$datapath,exdir=tempdir(),extras="-m")
    l <- length(list.files(paste(tempdir(),base,sep="/"),pattern="png$"))
    output$trials <- reactiveUI(function() {
      selectInput("trial", "Trial:", choices=1:l, selected=1)
    })
    output$time_range_slider <- reactiveUI(function() {
      base <- head(unlist(strsplit(input$archive$name,"\\.")),1)
      datafilename <- paste(tempdir(),base,sprintf("trial-%02d.txt", as.numeric(input$trial)),sep="/")
      d <- subset(read.delim(datafilename),state=="SEARCH")
      r <- range(d$system_time)
      sliderInput("time_range", label="", value=r, min=r[1], max=r[2])
    })
    l
  })
  output$fixationplot <- reactivePlot(function() {
    if (!is.null(input$time_range)) {
      base <- head(unlist(strsplit(input$archive$name,"\\.")),1)
      datafilename <- paste(tempdir(),base,sprintf("trial-%02d.txt", as.numeric(input$trial)),sep="/")
      d <- subset(read.delim(datafilename),state=="SEARCH" & system_time>=min(input$time_range) & system_time<=max(input$time_range))
      rimg <- as.raster(readPNG(paste(tempdir(),base,sprintf("trial-%02d.png", as.numeric(input$trial)),sep="/"),FALSE))
      rimg <- rimg[,315:1365]
      p1 <- xyplot(smi_syl~smi_sxl,data=subset(d, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0), scales=list(draw=F),
        col="blue", type="b", aspect=1, ylim=c(0,1050), xlim=c(315,1365),main=paste("Trial",input$trial,sep=" "),ylab="",xlab="",
        panel=function(...) {
          grid.raster(rimg)
          panel.xyplot(...)
      })
      p1 <- p1 + xyplot(smi_fy~smi_fx,data=subset(d, smi_type=="r"), col="red", aspect=1, ylim=c(0,1050), xlim=c(315,1365),scales=list(draw=F))
      p1 <- p1 + xyplot(mouse_y~mouse_x,data=subset(d, event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET"), type="b", col="green", aspect=1, ylim=c(0,1050), xlim=c(315,1365), scales=list(draw=F))
      print(p1)
    }
  })
})