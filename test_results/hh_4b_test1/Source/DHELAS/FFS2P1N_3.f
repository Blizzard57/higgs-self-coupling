C     This File is Automatically generated by ALOHA 
C     The process calculated in this file is: 
C     Identity(2,1)
C     
      SUBROUTINE FFS2P1N_3(F1, F2, COUP,S3)
      IMPLICIT NONE
      COMPLEX*16 CI
      PARAMETER (CI=(0D0,1D0))
      COMPLEX*16 COUP
      COMPLEX*16 F1(*)
      COMPLEX*16 F2(*)
      COMPLEX*16 S3(3)
      COMPLEX*16 TMP0
      TMP0 = (F2(3)*F1(3)+F2(4)*F1(4)+F2(5)*F1(5)+F2(6)*F1(6))
      S3(3)= COUP*(-CI )* TMP0
      END


