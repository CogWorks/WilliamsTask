library(grid)
library(png)
library(latticeExtra)
library(rjson)
library(shiny)


colors <- brewer.pal(3, "Set1")
pch <- 20
alpha <- 1

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
    start <- min(d$system_time)
    d$search_time = (d$system_time - start)
    rimg <- as.raster(readPNG(paste(tempdir(),ai$base,sprintf("trial-%02d.png", as.numeric(input$trial)),sep="/"),FALSE))
    rimg <- rimg[,315:1365]
    shapes <- fromJSON(paste(tempdir(),ai$base,sprintf("trial-%02d.json", as.numeric(input$trial)),sep="/"))
    list(data=d,rimg=rimg,shapes=shapes)
  })
  
  output$trials <- reactiveUI(function() {
    ai <- archiveInfo()
    if (is.null(ai)) return(NULL)
    selectInput("trial", "Trial:", choices=1:ai$ntrials, selected=1)
  })
  
  output$time_slider <- reactiveUI(function() {
    td <- trialData()
    if (is.null(td)) return(NULL)
    r <- range(td$data$search_time)
    sliderInput("time_slider","Time Range:",min=r[1],max=r[2],value=r)
  })
  
  basePlot <- reactive(function() {
    if (is.null(input$time_slider)) return(NULL)
    td <- trialData()
    pi <- td$shapes$probe
    ps <- td$shapes[[td$shapes$probe$id]]
    target <- c(ps$size,ps$color,ps$shape,ps$id)
    cues <- NULL
    if (pi$size) cues <- c(cues, ps$size)
    if (pi$color) cues <- c(cues, ps$color)
    if (pi$shape) cues <- c(cues, ps$shape)
    cues <- c(cues, ps$id)
    t1 <- paste("The target shape is:",paste(target,collapse=" "), sep=" ")
    t2 <- paste("The probe is:",paste(cues,collapse=" "), sep=" ")
    subtext <- paste(t1,t2,sep="\n")
    xyplot(smi_syl~smi_sxl,
      data=subset(td$data, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0),
      scales=list(draw=F), col="blue", type="b", aspect=1, ylab="",xlab="",
      ylim=c(0,1050), xlim=c(315,1365),sub=subtext,
      panel=function(...) {
        grid.raster(td$rimg)
      }
    )
  })
  
  samplesPlot <- reactive(function() {
    if (is.null(input$time_slider)) return(NULL)
    td <- trialData()
    xyplot(smi_syl~smi_sxl,
           data=subset(td$data, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0 & search_time>=min(input$time_slider) & search_time<=max(input$time_slider)),
           scales=list(draw=F), type="b", aspect=1, ylab="",xlab="",
           ylim=c(0,1050), xlim=c(315,1365), par.settings=custom.theme(symbol=colors[2],pch=pch,alpha=alpha)
    )
  })
  
  fixationsPlot <- reactive(function() {
    if (is.null(input$time_slider)) return(NULL)
    td <- trialData()
    xyplot(smi_fy~smi_fx,data=subset(td$data, smi_type=="r" & search_time>=min(input$time_slider) & search_time<=max(input$time_slider)),
           aspect=1, ylim=c(0,1050), xlim=c(315,1365),scales=list(draw=F),
           par.settings=custom.theme(symbol=colors[1],pch=pch,alpha=alpha))
  })
  
  mousePlot <- reactive(function() {
    if (is.null(input$time_slider)) return(NULL)
    td <- trialData()
    xyplot(mouse_y~mouse_x,
           data=subset(td$data, (event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET") & search_time>=min(input$time_slider) & search_time<=max(input$time_slider)),
           type="b", aspect=1, ylim=c(0,1050), xlim=c(315,1365), scales=list(draw=F),
           par.settings=custom.theme(symbol=colors[3],pch=pch,alpha=alpha))
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