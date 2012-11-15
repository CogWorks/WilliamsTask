require(signal)

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

plot_samples <- function(d, samplerate=1/500, p=3, n = p + 3 - p%%2) {
  d <- subset(d,event_type=="ET_SPL" & smi_dxl!=0 & smi_dxr!=0 & smi_dyl!=0 & smi_dyr!=0)
  d$ax = subtendedAngle(d$smi_sxl, 525, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
  d$ay = subtendedAngle(840, d$smi_syl, 840, 525, d$smi_exl, d$smi_eyl, d$smi_ezl, 1680, 1050, 473.76, 296.1)
  m <- min(d$smi_time)
  d$smi_time <- (d$smi_time - m) / 1000
  vx <- sgolayfilt(d$smi_sxl,n=n,p=p,m=1,ts=samplerate)
  vy <- sgolayfilt(d$smi_syl,n=n,p=p,m=1,ts=samplerate)
  v <- sqrt(vx*vx+vy*vy) / 231.086
  ax <- sgolayfilt(d$smi_sxl,n=n,p=p,m=2,ts=samplerate)
  ay <- sgolayfilt(d$smi_syl,n=n,p=p,m=2,ts=samplerate)
  a <- sqrt(ax*ax+ay*ay) / 231.086
  p1 <- xyplot(v~smi_time,d,type="l")#, auto.key=list(space="top",columns=2))#, xlim=c(0,.2), ylim=c(0,1000))
  p2 <- xyplot(a~smi_time,d,type="l")#, auto.key=list(space="top",columns=2))#, xlim=c(0,.2), ylim=c(0,100000))
  print(c(p1,p2))
}