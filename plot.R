require(latticeExtra)
require(grid)
require(png)
require(signal)
require(pastecs)
require(rjson)

colors <- brewer.pal(3, "Set1")
pch <- 20
alpha <- 1

distance2point <- function( x, y, vx, vy, vz, rx, ry, sw, sh ) {
  dx <- x / rx * sw - rx / 2.0 + vx
  dy <- y / ry * sh - ry / 2.0 - vy
  sd <- sqrt( dx ** 2 + dy ** 2 )
  sqrt( vz ** 2 + sd ** 2 )
}

subtendedAngle <- function( x1, y1, x2, y2, vx, vy, vz, rx, ry, sw, sh ) {
  d1 <- distance2point( x1, y1, vx, vy, vz, rx, ry, sw, sh )
  d2 <- distance2point( x2, y2, vx, vy, vz, rx, ry, sw, sh )
  dX <- sw * ( ( x2 - x1 ) / rx )
  dY <- sh * ( ( y2 - y1 ) / ry )
  dS <- sqrt( dX ** 2 + dY ** 2 )
  w1 <- d1 ** 2 + d2 ** 2 - dS ** 2
  w2 <- 2 * d1 * d2
  ( acos(w1/w2) / ( 2 * pi ) ) * 360
}

classify <- function(d, s=5.75, vpt=100) {
  cont = T
  print(vpt)
  while (cont) {
    f <- d$velocity[which(d$velocity<vpt)]
    vptn <- mean(f) + s * sd(f)
    if (abs(vptn-vpt)<1)
      cont <- F
    vpt <- vptn
    print(vpt)
  }
  return(list(velocity=vpt))
}

thresholds <- function(d, s=6, vpt=100) {
  cont = T
  while (cont) {
    f <- d$v[which(d$v<vpt)]
    vptn <- mean(f) + s * sd(f)
    if (abs(vptn-vpt)<1)
      cont <- F
    vpt <- vptn
  }
  print(vpt)
  return(list(velocity=vpt))
}

process_trials <- function(folder, p=3, n = p + 3 - p%%2, ts=.002) {
  combined <- NULL
  for (file in list.files(pattern="txt$")) {
    path <- paste(folder,file,sep="/")
    d <- subset(read.delim(path), state=="SEARCH" & event_type=="ET_SPL" & 
      smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0)
    sx <- sgolayfilt(d$smi_sxl,n=n,p=p,m=0,ts=ts)
    sy <- sgolayfilt(d$smi_syl,n=n,p=p,m=0,ts=ts)
    ax = subtendedAngle(sx, 525, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
    ay = subtendedAngle(840, sy, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
    svx <- sgolayfilt(ax,n=n,p=p,m=1,ts=ts)
    svy <- sgolayfilt(ay,n=n,p=p,m=1,ts=ts)
    velocity <- sqrt(svx**2+svy**2)
    sax <- sgolayfilt(ax,n=n,p=p,m=2,ts=ts)
    say <- sgolayfilt(ay,n=n,p=p,m=2,ts=ts)
    acceleration <- sqrt(sax**2+say**2)
    start <- min(d$smi_time)
    data <- data.frame(
      trial=d$trial,time=(d$smi_time-start)/1000,
      x=sx,y=sy,vx=svx,vy=svy,ax=sax,ay=say,
      v=velocity,a=acceleration
      )
    combined <- rbind(combined, data)
  }
  #return(combined)
  return(list(data=combined,thresholds=thresholds(combined)))
}

plot_trial <- function(archive, trial=1, samplerate=1, phi=1, p=3, n = p + 3 - p%%2, ts=1) {
  if (length(grep(".tar.gz$", archive))) {
    file <- tail(unlist(strsplit(archive,"/")),1)
    base <- head(unlist(strsplit(file,"\\.")),1)
    log <- paste(base,sprintf("trial-%02d.txt", trial),sep="/")
    img <- paste(base,sprintf("trial-%02d.png", trial),sep="/")
    suppressWarnings(
      json <- fromJSON(file=paste(base,sprintf("trial-%02d.json", trial),sep="/"))
    )
    untar(archive,compressed="gzip",exdir=tempdir(), extras="-m",files=c(log,img))
    d <- subset(read.delim(paste(tempdir(),log,sep="/")), state=="SEARCH")
    rimg <- as.raster(readPNG(paste(tempdir(),img,sep="/"), FALSE))
    unlink(paste(tempdir(),base,sep="/"),T,T)
  } else {
    log <- sprintf("trial-%02d.txt", trial)
    img <- sprintf("trial-%02d.png", trial)
    json <- sprintf("trial-%02d.json", trial)
    d <- subset(read.delim(paste(archive,log,sep="/")), state=="SEARCH")
    rimg <- as.raster(readPNG(paste(archive,img,sep="/"), FALSE))
    suppressWarnings(
      json <- fromJSON(file=paste(archive,json,sep="/"))
    )
  }
  d <- subset(d, event_type=="ET_SPL")# & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0)
  d$sx <- sgolayfilt(d$smi_sxl,n=n,p=p,m=0,ts=ts)
  d$sy <- sgolayfilt(d$smi_syl,n=n,p=p,m=0,ts=ts)
  d$ax = subtendedAngle(d$sx, 525, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
  d$ay = subtendedAngle(840, d$sy, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
  m <- min(d$smi_time)
  d$smi_time <- (d$smi_time - m) / 1000
  vx <- sgolayfilt(d$ax,n=n,p=p,m=1,ts=ts)
  vy <- sgolayfilt(d$ay,n=n,p=p,m=1,ts=ts)
  d$velocity <- samplerate * phi * sqrt(vx*vx+vy*vy)
  ax <- sgolayfilt(d$ax,n=n,p=p,m=2,ts=ts)
  ay <- sgolayfilt(d$ay,n=n,p=p,m=2,ts=ts)
  d$acceleration <- samplerate * phi * sqrt(ax*ax+ay*ay)
  thresholds <- list(velocity=30,acceleration=8000)#classify(d, vpt=mean(d$velocity)+sd(d$velocity)*3)
  rimg <- rimg[,315:1365]
  ###
  d$colors = "blue"
  for (i in 1:length(d$velocity)) {
    if (d$velocity[i] >= thresholds$velocity) {
      d$colors[i] = "red"
      if (i>1 && d$velocity[i-1] < thresholds$velocity)
        d$colors[i-1] = "red"
    } else {
      if (i>1 && d$velocity[i-1] >= thresholds$velocity)
        d$colors[i] = "red"
    }
  }
  ###
  d$vel_peaks = F
  vp <- find_peaks(d$velocity, 30)
  #print(vp)
  d$vel_peaks[vp] = T
  d$vel_peak_ranges = in_peak_range(d$velocity, 30)
  d$accel_peaks = F
  ap <- find_peaks(d$acceleration, 8000)
  #print(ap)
  d$accel_peaks[ap] = T
  d$class <- get_classification(d$velocity,30,d$acceleration,8000)
  pi <- json$probe
  ps <- json[[json$probe$id]]
  target <- c(ps$size,ps$color,ps$shape,ps$id)
  cues <- NULL
  if (pi$size) cues <- c(cues, ps$size)
  if (pi$color) cues <- c(cues, ps$color)
  if (pi$shape) cues <- c(cues, ps$shape)
  cues <- c(cues, ps$id)
  t1 <- paste("The target shape is:",paste(target,collapse=" "), sep=" ")
  t2 <- paste("The probe is:",paste(cues,collapse=" "), sep=" ")
  subtext <- paste(t1,t2,sep="\n")
  p1 <- xyplot(sy~sx,data=d, aspect=1, xlab="",main=paste("Trial",d$trial[1],sep=" "),
               ylim=c(0,1050), xlim=c(315,1365), scales=list(draw=F), ylab="",pch=pch,sub=subtext,
               panel=function(...) {
                 grid.raster(rimg)
                 panel.xyplot(...,type="l",col="red")
                 panel.xyplot(...,type="p",col=ifelse(d$class==1,"red",ifelse(d$class==2,"orange","blue")))
               })
  #p1 <- p1 + xyplot(smi_fy~smi_fx,data=subset(d, smi_type=="r"), col="red", aspect=1, ylim=c(0,1050), xlim=c(315,1365))
  #p1 <- p1 + xyplot(mouse_y~mouse_x,data=subset(d, event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET"), type="b", col="green", aspect=1, ylim=c(0,1050), xlim=c(315,1365))
  p2 <- xyplot(velocity~smi_time,d,type="b",panel=function(...){
    panel.xyplot(...)
    panel.abline(h=thresholds$velocity,col="red")
  }, col=ifelse(d$vel_peak_ranges,"red","blue"),pch=20,cex=ifelse(d$vel_peaks,2,.5))
  p3 <- xyplot(acceleration~smi_time,d,type="b",panel=function(...){
    panel.xyplot(...)
    panel.abline(h=thresholds$acceleration,col="red")
  }, col=ifelse(d$accel_peaks,"red","blue"),pch=20,cex=ifelse(d$accel_peaks,2,.5))
  #print(p1, position=c(0,0,.5,1), more=T)
  #print(p2, position=c(.5,.5,1,1), more=T)
  #print(p3, position=c(.5,0,1,.5))
  print(p1)
  return(d)
}

find_peaks <- function(x, threshold) {
  ranges <- find_peak_ranges(x, threshold)
  peaks <- NULL
  for (i in 1:nrow(ranges)) {
    range <- ranges[i,1]:ranges[i,2]
    r <- x[range]
    peaks <- c(peaks,range[which(r==max(r))])
  }
  return(peaks)
}

find_peak_ranges <- function(x, threshold) {
  t <- which(x>=threshold)
  d <- diff(t)
  n <- which(d>mean(d))
  return(data.frame(begin=c(t[1],t[n+1]),end=c(t[n],tail(t,1))))
}

in_peak_range <- function(x, threshold) {
  ranges <- find_peak_ranges(x, threshold)
  inpeak <- rep(F,length(x))
  for (i in 1:nrow(ranges)) {
    range <- ranges[i,1]:ranges[i,2]
    range <- c(min(range)-1,range,max(range)+1)
    inpeak[range] <- T
  }
  return(inpeak)
}

get_classification <- function(vel, vthresh, acc, athresh) {
  class <- rep(0,length(vel))
  vranges <- find_peak_ranges(vel, vthresh)
  apeaks <- find_peaks(acc, athresh)
  for (i in 1:nrow(vranges)) {
    range <- vranges[i,1]:vranges[i,2]
    range <- c(min(range)-1,range,max(range)+1)
    sac <- FALSE
    for (p in apeaks) {
      if (p>=min(range) && p<=max(range)) {
        sac <- TRUE
        break
      }
    }
    if (sac)
      class[range] <- 1
    else
      class[range] <- 2
  }
  return(class)
}