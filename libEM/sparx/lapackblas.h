#include <math.h>

typedef int integer;
typedef float real;
typedef double doublereal;
typedef int logical;

typedef short flag;
typedef short ftnlen;
typedef short ftnint;

#define TRUE_ (1) 
#define FALSE_ (0)

#define abs(x) ((x) >= 0 ? (x) : -(x))
#define dabs(x) (doublereal)abs(x)
#define f2cmin(a,b) ((a) <= (b) ? (a) : (b))
#define f2cmax(a,b) ((a) >= (b) ? (a) : (b))
#define df2cmin(a,b) (doublereal)f2cmin(a,b)
#define df2cmax(a,b) (doublereal)f2cmax(a,b)


integer s_cmp(char *, char *, ftnlen, ftnlen);
void s_copy(char *a, char *b, ftnlen la, ftnlen lb);
double pow_ri(real *ap, integer *bp);
double r_sign(real *a, real *b);

integer ieeeck_(integer *ispec, real *zero, real *one);

integer ilaenv_(integer *ispec, char *name__, char *opts, integer *n1, 
	integer *n2, integer *n3, integer *n4, ftnlen name_len, ftnlen 
	opts_len);

real drand(void);

logical lsame_(char *ca, char *cb);

/* Subroutine */ int saxpy_(integer *n, real *sa, real *sx, integer *incx, 
	real *sy, integer *incy);

/* Subroutine */ int scopy_(integer *n, real *sx, integer *incx, real *sy, 
	integer *incy);

doublereal sdot_(integer *n, real *sx, integer *incx, real *sy, integer *incy);

/* Subroutine */ int sgemm_(char *transa, char *transb, integer *m, integer *
	n, integer *k, real *alpha, real *a, integer *lda, real *b, integer *
	ldb, real *beta, real *c__, integer *ldc);

/* Subroutine */ int sgemv_(char *trans, integer *m, integer *n, real *alpha, 
	real *a, integer *lda, real *x, integer *incx, real *beta, real *y, 
	integer *incy);

/* Subroutine */ int sger_(integer *m, integer *n, real *alpha, real *x, 
	integer *incx, real *y, integer *incy, real *a, integer *lda);

/* Subroutine */ int slae2_(real *a, real *b, real *c__, real *rt1, real *rt2);

/* Subroutine */ int slaev2_(real *a, real *b, real *c__, real *rt1, real *
	rt2, real *cs1, real *sn1);

doublereal slamch_(char *cmach);

doublereal slanst_(char *norm, integer *n, real *d__, real *e);

doublereal slansy_(char *norm, char *uplo, integer *n, real *a, integer *lda, 
	real *work);

doublereal slapy2_(real *x, real *y);

/* Subroutine */ int slarfb_(char *side, char *trans, char *direct, char *
	storev, integer *m, integer *n, integer *k, real *v, integer *ldv, 
	real *t, integer *ldt, real *c__, integer *ldc, real *work, integer *
	ldwork);

/* Subroutine */ int slarf_(char *side, integer *m, integer *n, real *v, 
	integer *incv, real *tau, real *c__, integer *ldc, real *work);

/* Subroutine */ int slarfg_(integer *n, real *alpha, real *x, integer *incx, 
	real *tau);

/* Subroutine */ int slarft_(char *direct, char *storev, integer *n, integer *
	k, real *v, integer *ldv, real *tau, real *t, integer *ldt);

/* Subroutine */ int slartg_(real *f, real *g, real *cs, real *sn, real *r__);

/* Subroutine */ int slascl_(char *type__, integer *kl, integer *ku, real *
	cfrom, real *cto, integer *m, integer *n, real *a, integer *lda, 
	integer *info);

/* Subroutine */ int slaset_(char *uplo, integer *m, integer *n, real *alpha, 
	real *beta, real *a, integer *lda);

/* Subroutine */ int slasr_(char *side, char *pivot, char *direct, integer *m,
	 integer *n, real *c__, real *s, real *a, integer *lda);

/* Subroutine */ int slasrt_(char *id, integer *n, real *d__, integer *info);

/* Subroutine */ int slassq_(integer *n, real *x, integer *incx, real *scale, 
	real *sumsq);

/* Subroutine */ int slatrd_(char *uplo, integer *n, integer *nb, real *a, 
	integer *lda, real *e, real *tau, real *w, integer *ldw);

doublereal snrm2_(integer *n, real *x, integer *incx);

/* Subroutine */ int srot_(integer *n, real *sx, integer *incx, real *sy, 
			   integer *incy, real *c__, real *s);


/* Subroutine */ int sorg2l_(integer *m, integer *n, integer *k, real *a, 
	integer *lda, real *tau, real *work, integer *info);

/* Subroutine */ int sorg2r_(integer *m, integer *n, integer *k, real *a, 
	integer *lda, real *tau, real *work, integer *info);

/* Subroutine */ int sorgql_(integer *m, integer *n, integer *k, real *a, 
	integer *lda, real *tau, real *work, integer *lwork, integer *info);

/* Subroutine */ int sorgqr_(integer *m, integer *n, integer *k, real *a, 
	integer *lda, real *tau, real *work, integer *lwork, integer *info);

/* Subroutine */ int sorgtr_(char *uplo, integer *n, real *a, integer *lda, 
	real *tau, real *work, integer *lwork, integer *info);

/* Subroutine */ int sscal_(integer *n, real *sa, real *sx, integer *incx);

/* Subroutine */ int ssteqr_(char *compz, integer *n, real *d__, real *e, 
	real *z__, integer *ldz, real *work, integer *info);

/* Subroutine */ int ssterf_(integer *n, real *d__, real *e, integer *info);

/* Subroutine */ int sswap_(integer *n, real *sx, integer *incx, real *sy, 
	integer *incy);

/* Subroutine */ int ssyev_(char *jobz, char *uplo, integer *n, real *a, 
	integer *lda, real *w, real *work, integer *lwork, integer *info);

/* Subroutine */ int ssymv_(char *uplo, integer *n, real *alpha, real *a, 
	integer *lda, real *x, integer *incx, real *beta, real *y, integer *
	incy);

/* Subroutine */ int ssyr2_(char *uplo, integer *n, real *alpha, real *x, 
	integer *incx, real *y, integer *incy, real *a, integer *lda);

/* Subroutine */ int ssyr2k_(char *uplo, char *trans, integer *n, integer *k, 
	real *alpha, real *a, integer *lda, real *b, integer *ldb, real *beta,
	 real *c__, integer *ldc);

/* Subroutine */ int ssytd2_(char *uplo, integer *n, real *a, integer *lda, 
	real *d__, real *e, real *tau, integer *info);

/* Subroutine */ int ssytrd_(char *uplo, integer *n, real *a, integer *lda, 
	real *d__, real *e, real *tau, real *work, integer *lwork, integer *
	info);

/* Subroutine */ int strmm_(char *side, char *uplo, char *transa, char *diag, 
	integer *m, integer *n, real *alpha, real *a, integer *lda, real *b, 
	integer *ldb);

/* Subroutine */ int strmv_(char *uplo, char *trans, char *diag, integer *n, 
	real *a, integer *lda, real *x, integer *incx);

/* Subroutine */ int xerbla_(char *srname, integer *info);

/* Subroutine */ int sstedc_(char *compz, integer *n, real *d__, real *e, 
	real *z__, integer *ldz, real *work, integer *lwork, integer *iwork, 
			     integer *liwork, integer *info);

/* Subroutine */ int sstevd_(char *jobz, integer *n, real *d__, real *e, real 
	*z__, integer *ldz, real *work, integer *lwork, integer *iwork, 
			     integer *liwork, integer *info);

/* Subroutine */ int slaeda_(integer *n, integer *tlvls, integer *curlvl, 
	integer *curpbm, integer *prmptr, integer *perm, integer *givptr, 
	integer *givcol, real *givnum, real *q, integer *qptr, real *z__, 
			     real *ztemp, integer *info);

/* Subroutine */ int slaed0_(integer *icompq, integer *qsiz, integer *n, real 
	*d__, real *e, real *q, integer *ldq, real *qstore, integer *ldqs, 
			     real *work, integer *iwork, integer *info);

/* Subroutine */ int slaed1_(integer *n, real *d__, real *q, integer *ldq, 
	integer *indxq, real *rho, integer *cutpnt, real *work, integer *
			     iwork, integer *info);

/* Subroutine */ int slaed2_(integer *k, integer *n, integer *n1, real *d__, 
	real *q, integer *ldq, integer *indxq, real *rho, real *z__, real *
	dlamda, real *w, real *q2, integer *indx, integer *indxc, integer *
			     indxp, integer *coltyp, integer *info);

/* Subroutine */ int slaed3_(integer *k, integer *n, integer *n1, real *d__, 
	real *q, integer *ldq, real *rho, real *dlamda, real *q2, integer *
			     indx, integer *ctot, real *w, real *s, integer *info);

/* Subroutine */ int slaed4_(integer *n, integer *i__, real *d__, real *z__, 
			     real *delta, real *rho, real *dlam, integer *info);

/* Subroutine */ int slaed5_(integer *i__, real *d__, real *z__, real *delta, 
			     real *rho, real *dlam);

/* Subroutine */ int slaed6_(integer *kniter, logical *orgati, real *rho, 
			     real *d__, real *z__, real *finit, real *tau, integer *info);

/* Subroutine */ int slaed7_(integer *icompq, integer *n, integer *qsiz, 
	integer *tlvls, integer *curlvl, integer *curpbm, real *d__, real *q, 
	integer *ldq, integer *indxq, real *rho, integer *cutpnt, real *
	qstore, integer *qptr, integer *prmptr, integer *perm, integer *
	givptr, integer *givcol, real *givnum, real *work, integer *iwork, 
			     integer *info);

/* Subroutine */ int slaed8_(integer *icompq, integer *k, integer *n, integer 
	*qsiz, real *d__, real *q, integer *ldq, integer *indxq, real *rho, 
	integer *cutpnt, real *z__, real *dlamda, real *q2, integer *ldq2, 
	real *w, integer *perm, integer *givptr, integer *givcol, real *
			     givnum, integer *indxp, integer *indx, integer *info);

/* Subroutine */ int slaed9_(integer *k, integer *kstart, integer *kstop, 
	integer *n, real *d__, real *q, integer *ldq, real *rho, real *dlamda,
			     real *w, real *s, integer *lds, integer *info);


/* Subroutine */ int slacpy_(char *uplo, integer *m, integer *n, real *a, 
			     integer *lda, real *b, integer *ldb);

/* Subroutine */ int slamrg_(integer *n1, integer *n2, real *a, integer *
			     strd1, integer *strd2, integer *index);





