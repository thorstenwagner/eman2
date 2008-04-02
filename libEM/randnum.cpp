/**
 * $Id$
 */
 
/*
* Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
* Copyright (c) 2000-2006 Baylor College of Medicine
* 
* This software is issued under a joint BSD/GNU license. You may use the
* source code in this file under either license. However, note that the
* complete EMAN2 and SPARX software packages have some GPL dependencies,
* so you are responsible for compliance with the licenses of these packages
* if you opt to use BSD licensing. The warranty disclaimer below holds
* in either instance.
* 
* This complete copyright notice must be included in any revised version of the
* source code. Additional authorship citations may be added, but existing
* author citations must be preserved.
* 
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
* 
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
* 
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
* 
* */

#include <cmath>
#include <ctime>
#include <cstdio>
#include <sys/time.h>
#include "randnum.h"
 
using namespace EMAN;

Randnum * Randnum::_instance = 0;
const gsl_rng_type * Randnum::T = gsl_rng_default;
gsl_rng * Randnum::r = 0;

unsigned long int Randnum::random_seed()
{
	unsigned int seed;
	struct timeval tv;
	FILE *devrandom;

	if ((devrandom = fopen("/dev/random","r")) == NULL) {
		gettimeofday(&tv,0);
		seed = tv.tv_sec + tv.tv_usec;
		//printf("Got seed %u from gettimeofday()\n",seed);
	} 
	else {
		fread(&seed,sizeof(seed),1,devrandom);
		//printf("Got seed %u from /dev/random\n",seed);
		fclose(devrandom);
	}

	return seed;
}

Randnum * Randnum::Instance() {
	if(_instance == 0) {
		_instance = new Randnum();
	}
	
	return _instance; 
}

Randnum * Randnum::Instance(const gsl_rng_type * _t) {
	if(_instance == 0) {
		_instance = new Randnum(_t);
	}
	else if(_t != _instance->T) {
		gsl_rng_free (_instance->r);
		_instance->r = gsl_rng_alloc (_t);
//		gsl_rng_set(_instance->r, random_seed() );
	}
	
	return _instance;
}

Randnum::Randnum()
{
	r = gsl_rng_alloc (T);	
//	gsl_rng_set(r, random_seed() );	
	gsl_rng_set(r, 0);
}

Randnum::Randnum(const gsl_rng_type * _t)
{
	r = gsl_rng_alloc (_t);	
//	gsl_rng_set(r, random_seed() );
}

Randnum::~Randnum()
{
	gsl_rng_free (r);
}

void Randnum::set_seed(unsigned long int seed)
{
	gsl_rng_set(r, seed);
}

long Randnum::get_irand(long lo, long hi) const
{
	return gsl_rng_uniform_int(r, hi-lo+1)+lo;
}

float Randnum::get_frand(double lo, double hi) const
{
	return static_cast<float>(gsl_rng_uniform(r) * (hi -lo) + lo);
}

float Randnum::get_frand_pos(double lo, double hi) const
{
	return static_cast<float>(gsl_rng_uniform_pos(r) * (hi -lo) + lo);
}

float Randnum::get_gauss_rand(float mean, float sigma) const
{
	float x = 0.0f;
	float y = 0.0f;
	float r = 0.0f;
	bool valid = true;
	
	while (valid) {
		x = get_frand_pos(-1.0, 1.0);
		y = get_frand_pos(-1.0, 1.0);
		r = x * x + y * y;
		
		if (r <= 1.0 && r > 0) {
			valid = false;
		}
	}
	
	float f = std::sqrt(-2.0f * std::log(r) / r);
	float result = x * f * sigma + mean;
	return result;
}

void Randnum::print_generator_type() const
{
	const gsl_rng_type **t, **t0;
          
	t0 = gsl_rng_types_setup ();
          
	printf ("Available generators:\n");
          
	for (t = t0; *t != 0; t++) {
		printf ("%s\n", (*t)->name);
	}	
}
