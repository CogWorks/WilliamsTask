require(latticeExtra)
require(grid)
require(png)

plot_trial <- function(archive, trial) {
  file <- tail(unlist(strsplit(archive,"/")),1)
  base <- head(unlist(strsplit(file,"\\.")),1)
  log <- paste(base,sprintf("trial-%02d.txt", trial),sep="/")
  img <- paste(base,sprintf("trial-%02d.png", trial),sep="/")
  untar(archive,compressed="gzip",exdir=tempdir(), extras="-m",files=c(log,img))
  d <- subset(read.delim(paste(tempdir(),log,sep="/")), state=="SEARCH")
  rimg <- readPNG(paste(tempdir(),img,sep="/"), FALSE)
  p1 <- xyplot(smi_syl~smi_sxl,data=subset(d, event_type=="ET_SPL" & smi_dyl!=0 & smi_dyr!=0 & smi_dxl!=0 & smi_dxr!=0),
               col="blue", type="b", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680),
               panel=function(...) {
                 grid.raster(as.raster(rimg))
                 panel.xyplot(...)
               })
  p1 <- p1 + xyplot(smi_fy~smi_fx,data=subset(d, smi_type=="r"), col="red", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680))
  p1 <- p1 + xyplot(mouse_y~mouse_x,data=subset(d, event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET"), type="b", col="green", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680))
  print(p1)
  unlink(paste(tempdir(),base,sep="/"),T,T)
}